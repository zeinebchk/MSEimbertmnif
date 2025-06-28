from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func, join, cast, String
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
    dateLancement = db.Column(db.Date, nullable=True)
    dateCreation=db.Column(db.Date, nullable=True)
    etat=db.Column(db.String(20), nullable=True)

    ofs_chaines = relationship("OFSChaine", back_populates="ofs")
    def updateEtatAndDateLancement(self):
        self.etat="lancée"
        self.dateLancement=datetime.now().date()
        db.session.commit()
    @classmethod
    def get_of_by_numOF(cls, numOF):
        return cls.query.filter_by(numOF=numOF).first()
    def save_of(self):
        db.session.add(self)
        db.session.commit()
    @classmethod
    def get_all_latest_ofs(cls):
        latest_date = db.session.query(func.max(OFS.dateCreation)).scalar()
        return cls.query.filter_by(dateCreation=latest_date,dateLancement=None).all()

    @classmethod
    def get_all_nonlance_ofs(cls):
        return cls.query.filter_by(etat="nonLance").all()
    @classmethod
    def get_ofs_by_lancementDate(cls, dateLancement):
        return cls.query.filter_by(dateLancement=dateLancement).all()

    @classmethod
    def get_ofs_chaines(cls,prefix=None):
        query = db.session.query(
            OFS.numOF,
            OFS.Pointure,
            OFS.Quantite,
            OFS.Modele,
            OFS.Coloris,
            OFS.SAIS,
            OFS.dateLancement,
            OFS.etat,
            func.group_concat(OFSChaine.idChaine.op('ORDER BY')(OFSChaine.idChaine), ',').label('parcours')
        ).join(OFSChaine, OFS.numOF == OFSChaine.numCommandeOF)
        if prefix:
            query = query.filter(cast(OFS.numOF, String).like(f"{prefix}%"))
        query = query.group_by(OFS.numOF,
                               OFS.Pointure,
                               OFS.Quantite,
                               OFS.Modele,
                               OFS.Coloris,
                               OFS.SAIS,
                               OFS.dateLancement,
                               OFS.etat)

        return query.all()

    @classmethod
    def get_inprogress_ofs(cls, prefix,idchaine):
        return cls.query.filter(
            cls.etat == "enCours",
            cls.id_chaine==idchaine,
            cast(cls.numOF, String).like(f"{prefix}%")
        ).all()

    @classmethod
    def get_inprogress_ofs(cls, prefix, idchaine):
        return cls.query.filter(
            cls.etat == "enAttente",
            cls.id_chaine == idchaine,
            cast(cls.numOF, String).like(f"{prefix}%")
        ).all()

    @classmethod
    def get_inprogress_ofs(cls, prefix, idchaine):
        return cls.query.filter(
            cls.etat == "termine",
            cls.id_chaine == idchaine,
            cast(cls.numOF, String).like(f"{prefix}%")
        ).all()

    @classmethod
    def get_ofs_by_modele(cls, num):
        pattern = f"_{num}%"  # Exemple : _2% ⇒ le 2e chiffre est "2"

        return (
            db.session.query(
                cls.Modele,
                cls.Coloris,
                cls.dateCreation,
                func.sum(cls.Quantite).label("total_quantite"),
                func.count(cls.numOF).label("total_ofs")
            )
            .filter(cast(cls.numOF, String).like(pattern))
            .group_by(cls.Modele, cls.Coloris, cls.dateCreation)
            .all()
        )

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
    def save_chaine_of(self):
        db.session.add(self)
        db.session.commit()

    def delete_of_chaine(self):
        db.session.delete(self)
        db.session.commit()
    @classmethod
    def get_ofs_chaine_by_numOF(cls,numOf,idch):
        return cls.query.filter_by(numCommandeOF=numOf,idChaine=idch).first()





class  Ouvriers(db.Model):
    __tablename__ = 'ouvriers'
    MATR=db.Column(db.Integer, primary_key=True)
    NOM=db.Column(db.String(20), nullable=False)
    PRENOM=db.Column(db.String(20), nullable=False)

    @classmethod
    def get_ouvrier_by_MATR(cls, MATR):
        return cls.query.filter_by(MATR=MATR).first()

    def save_user(self):
        db.session.add(self)
        db.session.commit()

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()

    def update_user(self, new_data):
        for key, value in new_data.items():
            setattr(self, key, value)
            # met à jour chaque attribut
        db.session.commit()

    @classmethod
    def get_user_byId(cls, id):
        return cls.query.filter_by(MATR=id).first()

    @classmethod
    def get_all_users(self):
        return User.query.all()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "authorized": self.authorized,
            # ajoute d'autres champs si besoin
        }

class ouvrier_chaine_ofs(db.Model):
    __tablename__ = 'ouvrier_chaine_ofs'
    idChaine = db.Column(db.String(20), db.ForeignKey('type_chaine.id'), primary_key=True)
    numCommandeOF = db.Column(db.Integer, db.ForeignKey('ofs.numOF'), primary_key=True)
    matOuvrier = db.Column(db.Integer, db.ForeignKey('ouvriers.MATR'), primary_key=True)




