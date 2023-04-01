from marshmallow import Schema, fields


class FilesSchema(Schema):
    id = fields.Int(dump_only=True)
    img = fields.Str(required=True,)
    mimetype = fields.Str()

class FilesUpdateSchema(Schema):
    id = fields.Int()
    img = fields.Str()
    mimetype = fields.Str()


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
