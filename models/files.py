from db import db


class FilesModel(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=True)
    mimetype = db.Column(db.Text, nullable=False)
