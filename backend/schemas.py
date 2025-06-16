from marshmallow import Schema, fields


class UserSchema(Schema):
    __tablename__ = 'users'

    id = fields.Integer()
    username =fields.String()
    role =fields.String()

