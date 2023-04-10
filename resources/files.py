from flask.views import MethodView
from flask import Flask, request, Response, jsonify
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import FilesModel, UserModel
from schemas import FilesSchema, FilesUpdateSchema

import filetype

blp = Blueprint("Files", "files", description="Operations on files")


@blp.route("/")
class Home(MethodView):
    def get(self):

        return Response(response = "Service is running.",status = 200)


@blp.route('/upload')
class UploadFile(MethodView):
    @jwt_required()
    #@blp.response(201, FilesSchema)
    def post(self):
        """This method is to files to the database"""
        logging.info('printing file details')
        logging.info(request.files['file'])
        file = request.files['file']

        if not file:
            return Response( response = 'No pic uploaded!', status = 400)

        else:
            mimetype = file.mimetype

            try:
                file_extension = file.filename.rsplit('.', 1)[1].lower() # get the file extension
                content_type = request.headers['Content-Type'].split(';')[0]

            except IndexError:
                return Response(response='File type not supported. Upload .jpg, .jpeg, .png or .pdf only', status=415)

            if file_extension in ['jpg', 'jpeg', 'png', 'pdf'] and mimetype in ('application/pdf', 'image/jpeg', 'image/png') and content_type in ['multipart/form-data']:

                file_info = filetype.guess(file)

                if file_info is not None:
                    file_ext = file_info.extension

                    if file_ext in ['png', 'jpg', 'pdf']: #or file_type == 'application/pdf':

                        img = FilesModel(img=file.read(), mimetype=mimetype)

                        try:
                            db.session.add(img)
                            db.session.commit()
                            val = img.id
                            data = {"id": val,
                                "status": "200 OK",
                                "status_code": 200
                        }
                        except SQLAlchemyError:
                            abort(500, message="An error occurred while inserting the file")

                        return jsonify(data)
                    else:
                        return Response(response='File type not supported. Upload .jpg, .jpeg, .png or .pdf only', status=415)
                else:
                    return Response(response='File type not supported. Upload .jpg, .jpeg, .png or .pdf only', status=415)
            else:

                return Response(response='File type not supported. Upload .jpg, .jpeg, .png or .pdf only', status=415)


@blp.route('/get/<int:id>')
class GetFile(MethodView):
    @jwt_required()
    def get(self,id):
        """This method returns the file corresponding to the id"""

        img = FilesModel.query.filter_by(id=id).first()
        if not img:
            return Response( response = 'Img Not Found!', status = 404)

        return Response(img.img, mimetype=img.mimetype)


    # @jwt_required()
    # #@blp.arguments(FilesUpdateSchema)
    # #@blp.response(200, FilesSchema)
    # def put(self,id):
    #     """This method is to update the Aadhaar file"""
    #     img1 = FilesModel.query.get(id)

    #     file = request.files['file']
    #     mimetype = file.mimetype

    #     if img1:
    #         img1.img = file.read()
    #         img1.mimetype = mimetype
    #     else:
    #         img1 = FilesModel(img=file.read(), mimetype=mimetype)

    #     db.session.add(img1)
    #     db.session.commit()
    #     val = img1.id
    #     data = {"id": val,
    #         "status": "200 OK",
    #         "status_code": 200
    #         }

    #     return jsonify(data)



