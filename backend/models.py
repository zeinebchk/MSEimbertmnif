from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import relationship

from extension import db
from werkzeug.security import generate_password_hash, check_password_hash

class OFS(db.Model):
    __tablename__ = 'ofs'

    numOF = db.Column(db.Integer, primary_key=True)
    Pointure = db.Column(db.Integer, nullable=False)
    Quantite = db.Column(db.Integer, nullable=False)
    Modele = db.Column(db.String(20), nullable=False)
    Coloris = db.Column(db.String(20), nullable=False)
    SAIS = db.Column(db.String(20), nullable=False)
    dateLancement = db.Column(db.Date, nullable=False)

    ofs_chaines = relationship("OFSChaine", back_populates="ofs")
    def save_of(self):
        db.session.add(self)
        db.session.commit()
    @classmethod
    def get_all_latest_ofs(self):
        latest_date = db.session.query(func.max(OFS.dateLancement)).scalar()
        return OFS.query.filter_by(dateLancement=latest_date).all()
    @classmethod
    def get_ofs_by_lancementDate(self, dateLancement):
        return OFS.query.filter_by(dateLancement=dateLancement).all()

class TypeChaine(db.Model):
    __tablename__ = 'type_chaine'

    id = db.Column(db.String(20), primary_key=True)

    ofs_chaines = relationship("OFSChaine", back_populates="type_chaine")

    def save_chaine(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_all_chaines(self):
        return TypeChaine.query.all()

    @classmethod
    def get_type_chaine_byID(cls, id):
        return cls.query.filter_by(id=id).first()
    def to_dict(self):
        return {
            "id": self.id,
            # ajoute d'autres champs si besoin
        }
class User(db.Model):
    __tablename__ = 'users'


    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    pwd = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20),  nullable=False)
    authorized = db.Column(db.Integer, nullable=False)

    def generate_password(self, password):
        self.pwd = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.pwd, password)

    @classmethod
    def get_user_by_username(cls,username):
        return cls.query.filter_by(username=username).first()

    def save_user(self):
        db.session.add(self)
        db.session.commit()
    def delete_user(self):
        db.session.delete(self)
        db.session.commit()
    def update_user(self,new_data):
        for key, value in new_data.items():
            if key == "pwd":
                print(value)# Si on met à jour le mot de passe
                self.pwd = generate_password_hash(value)
                continue
            setattr(self, key, value)
            # met à jour chaque attribut
        db.session.commit()
    @classmethod
    def get_user_byId(cls,id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_users(self):
        return User.query.all()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "authorized":self.authorized,
            # ajoute d'autres champs si besoin
        }


class OFSChaine(db.Model):
    __tablename__ = 'ofs_chaine'

    idChaine = db.Column(db.String(20), db.ForeignKey('type_chaine.id'), primary_key=True)
    numCommandeOF = db.Column(db.Integer, db.ForeignKey('ofs.numOF'), primary_key=True)
    dateLancement_of_chaine = db.Column(db.Date)
    dateFin = db.Column(db.Date)
    etat = db.Column(db.String(20), nullable=False)

    type_chaine = relationship("TypeChaine", back_populates="ofs_chaines")
    ofs = relationship("OFS", back_populates="ofs_chaines")



class  Ouvriers(db.Model):
    __tablename__ = 'ouvriers'
    MATR=db.Column(db.Integer, primary_key=True)
    NOM=db.Column(db.String(20), nullable=False)
    PRENOM=db.Column(db.String(20), nullable=False)
class ouvrier_chaine_ofs(db.Model):
    __tablename__ = 'ouvrier_chaine_ofs'
    idChaine = db.Column(db.String(20), db.ForeignKey('type_chaine.id'), primary_key=True)
    numCommandeOF = db.Column(db.Integer, db.ForeignKey('ofs.numOF'), primary_key=True)
    matOuvrier = db.Column(db.Integer, db.ForeignKey('ouvriers.MATR'), primary_key=True)








