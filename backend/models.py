from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from extension import db
from werkzeug.security import generate_password_hash, check_password_hash

class OFS(db.Model):
    __tablename__ = 'ofs'

    numCommande = db.Column(db.Integer, primary_key=True)
    dateLancement = db.Column(db.Date, nullable=False)
    pointure = db.Column(db.Integer, nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    article = db.Column(db.String(20), nullable=False)

    ofs_chaines = relationship("OFSChaine", back_populates="ofs")


class TypeChaine(db.Model):
    __tablename__ = 'type_chaine'

    id = db.Column(db.String(20), primary_key=True)

    ofs_chaines = relationship("OFSChaine", back_populates="type_chaine")

class User(db.Model):
    __tablename__ = 'users'


    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    pwd = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


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
    def get_all_users(self):
        return User.query.all()

class OFSChaine(db.Model):
    __tablename__ = 'ofs_chaine'

    idChaine = db.Column(db.String(20), db.ForeignKey('type_chaine.id'), primary_key=True)
    numCommandeOF = db.Column(db.Integer, db.ForeignKey('ofs.numCommande'), primary_key=True)
    dateLancement_of_chaine = db.Column(db.Date)
    dateFin = db.Column(db.Date)
    etat = db.Column(db.String(20), nullable=False)
    MatOuvrier1 = db.Column(db.Integer)
    MatOuvrier2 = db.Column(db.Integer)

    type_chaine = relationship("TypeChaine", back_populates="ofs_chaines")
    ofs = relationship("OFS", back_populates="ofs_chaines")



