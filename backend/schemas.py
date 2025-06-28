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
    id = fields.String()

class OFSSchema(Schema):
    __tablename__ = 'ofs'
    numOF = fields.Integer()
    Pointure=fields.Integer()
    Quantite = fields.Integer()
    Modele = fields.String()
    Coloris = fields.String()
    SAIS = fields.String()
    dateLancement = fields.Date()
    dateCreation = fields.Date()
    etat = fields.String()

    class Meta:
        ordered = True
class GetOfsForUpdate(Schema):
    __tablename__ = 'ofs'
    numOF = fields.Integer()
    Pointure = fields.Integer()
    Quantite = fields.Integer()
    Modele = fields.String()
    Coloris = fields.String()
    SAIS = fields.String()
    dateLancement = fields.Date()
    etat = fields.String()
    parcours = fields.String()

class OFSChaineSchema(Schema):
    __tablename__ = 'ofs_chaine'

class GetOfsByModele(Schema):
    __tablename__ = 'ofs'
    Modele = fields.String()
    Coloris = fields.String()
    SAIS = fields.String()
    dateCreation = fields.Date()
    total_quantite=fields.Integer()
    total_ofs=fields.Integer()