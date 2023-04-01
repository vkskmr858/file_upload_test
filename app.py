import secrets
from flask import Flask, jsonify, request
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from config import *

from db import db
from models.TokenBlocklist import TokenBlocklistModel

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from models import UserModel, TokenBlocklistModel
from schemas import UserSchema

from datetime import datetime
from datetime import timedelta
from datetime import timezone

#from resources.user import blp as UserBlueprint
from resources.files import blp as FilesBlueprint

import ssl

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from password_strength import PasswordPolicy
from password_strength import PasswordStats

from functools import wraps
from config import API_KEY

import logging

policy = PasswordPolicy.from_names(
length=8,  # min length: 8
uppercase=2,  # need min. 2 uppercase letters
numbers=2,  # need min. 2 digits
special=2,  # need min. 2 special characters
)


app = Flask(__name__)
app.config["API_TITLE"] = "Aadhar Files REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config[
    "OPENAPI_SWAGGER_UI_URL"
] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
app.config["SQLALCHEMY_DATABASE_URI"] = DB_CRED
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000
app.config['RATELIMIT_STRATEGY'] = "fixed-window"

db.init_app(app)
api = Api(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    #default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)
#limiter.init_app(app)

app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_PUBLIC_KEY'] = open('public_key.pem').read()
app.config['JWT_PRIVATE_KEY'] = open('private_key.pem').read()


#app.config["JWT_SECRET_KEY"] = secrets.SystemRandom().getrandbits(128)
jwt = JWTManager(app)

# Callback function to check if a JWT exists in the database blocklist
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklistModel.id).filter_by(jti=jti).scalar()

    return token is not None


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )

@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {
                "description": "The token is not fresh.",
                "error": "fresh_token_required",
            }
        ),
        401,
    )

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return (
        jsonify(
            {"description": "The token has been revoked.", "error": "token_revoked"}
        ),
        401,
    )

# JWT configuration ends

with app.app_context():
    import models

    db.create_all()

#api.register_blueprint(UserBlueprint)
api.register_blueprint(FilesBlueprint)

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Api-Key')
        if api_key and api_key == API_KEY:
            return view_function(*args, **kwargs)
        else:
            abort(401, message="Invalid API key")
    return decorated_function


@app.route("/register", methods=["POST"])
#@limiter.limit("3/hour")
#@require_api_key
def UserRegister():
    print(request.get_json())
    user_data = request.get_json()
    total_users = UserModel.query.count()
    if total_users > 150:
        return {"message": "Total number of users exceeded"}
    else:
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="could not register user")

        else:
            policy_test = policy.test(user_data["password"])
            stats = PasswordStats(user_data["password"])

            if stats.strength() > 0.5 and not policy_test:
                user = UserModel(
                    username=user_data["username"],
                    password=pbkdf2_sha256.hash(user_data["password"]),
                )
                db.session.add(user)
                db.session.commit()

                return {"message": "User created successfully."}, 201

            else:

                return {"message": "weak password. Password length must be 8 characters long including 2 uppercase, 2 numbers and 2 special characters"}


@app.route("/login", methods=["POST"])
@limiter.limit("1/minute")
def login():

    client_ip = request.remote_addr
    print(f"Client IP address: {client_ip}")
    logging.info(client_ip)
    user_data = request.get_json()
    user = UserModel.query.filter(
        UserModel.username == user_data["username"]
    ).first()

    if user and pbkdf2_sha256.verify(user_data["password"], user.password):
        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}, 200

    abort(401, message="Invalid credentials.")


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklistModel(jti=jti, created_at=now))
    db.session.commit()
    return {"message": "Successfully logged out"}, 200


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user, fresh=False)
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklistModel(jti=jti, created_at=now))
    db.session.commit()
    return {"access_token": new_token}, 200

