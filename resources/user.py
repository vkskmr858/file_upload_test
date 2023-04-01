from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    get_jwt,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel, TokenBlocklistModel
from schemas import UserSchema

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from password_strength import PasswordPolicy
from password_strength import PasswordStats

from functools import wraps
from config import API_KEY

policy = PasswordPolicy.from_names(
length=8,  # min length: 8
uppercase=2,  # need min. 2 uppercase letters
numbers=2,  # need min. 2 digits
special=2,  # need min. 2 special characters
)
