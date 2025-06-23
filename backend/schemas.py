from marshmallow import Schema, fields


class UserSchema(Schema):
    __tablename__ = 'users'

    id = fields.Integer()
    username =fields.String()
    role =fields.String()
    password = fields.String()
    authorized = fields.Integer()
class ChaineSchema(Schema):
    __tablename__ = 'type_chaine'

class OFSSchema(Schema):
    __tablename__ = 'ofs'
    numOF = fields.Integer()
    quantite = fields.Integer()
    Modele = fields.String()
    COL = fields.String()
    SAIS = fields.String()
    dateLancement = fields.Date()

    id = fields.String()


