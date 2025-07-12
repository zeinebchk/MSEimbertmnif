from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, func, join, cast, String, case, distinct, Integer
from sqlalchemy.orm import relationship, aliased

from extension import db
from werkzeug.security import generate_password_hash, check_password_hash

class OFS(db.Model):
    __tablename__ = 'ofs'

    numOF = db.Column(db.Integer, primary_key=True)
    Pointure = db.Column(db.Integer, nullable=False)
    Quantite = db.Column(db.Integer, nullable=False)
    Modele = db.Column(db.String(100), nullable=False)
    Coloris = db.Column(db.String(20), nullable=False)
    SAIS = db.Column(db.String(20), nullable=False)
    dateLancement = db.Column(db.Date, nullable=True)
    dateCreation=db.Column(db.Date, nullable=True)
    etat=db.Column(db.String(20), nullable=True)
    inventaire=db.Column(db.String(20), nullable=True)
    magasin=db.Column(db.String(20), nullable=True)
    nbre=db.Column(db.Integer, nullable=True)
    colisNonEmb=db.Column(db.Integer, nullable=True)
    DF=db.Column(db.Date, nullable=True)
    observation=db.Column(db.String(20), nullable=True)
    export=db.Column(db.String(20), nullable=True)

    ofs_chaines = relationship("OFSChaine", back_populates="ofs")

    def update_of(self,new_data):
        for key, value in new_data.items():
            if key.lower() == "df" and isinstance(value, str):
                try:
                    # Convertit la chaîne '02/07/2025' en objet date
                    value = datetime.strptime(value, "%d/%m/%Y").date()

                except ValueError:
                    continue  # Ignore si format invalide
            if key.lower() == "nbre" and isinstance(value, str):
                try:
                    value=int(value)
                    # Convertit la chaîne '02/07/2025' en objet date
                    self.colisNonEmb=self.colisNonEmb-value

                except ValueError:
                    continue  # Ignore si format invalide
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
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
                cls.SAIS,
                func.sum(cls.Quantite).label("total_quantite"),
                func.count(cls.numOF).label("total_ofs")
            )
            .filter(cast(cls.numOF, String).like(pattern))
            .group_by(cls.Modele, cls.Coloris, cls.dateCreation, cls.SAIS)
            .all()
        )
    @classmethod
    def get_maximum_date_of_ofs(self):
        numof_str = cast(OFS.numOF, String)

        # Longueur de numOF
        length_numof = func.length(numof_str)

        # Extraire les 3 chiffres selon la longueur
        substring_cond = case(
            (length_numof == 6, func.substr(numof_str, 2, 3)),
            (length_numof == 8, func.substr(numof_str, 4, 3)),
            else_=func.substr(numof_str, 2, 3)  # fallback
        )

        # Convertir en entier pour comparaison
        substring_as_int = cast(substring_cond, Integer)

        # Requête : maximum de ces valeurs
        max_val = db.session.query(func.max(substring_as_int)).scalar()
        return max_val

    @classmethod
    def get_all_ofs_by_modele(cls,modele):
        coupe = aliased(OFSChaine)
        piqure = aliased(OFSChaine)
        montage = aliased(OFSChaine)

        query = (
            db.session.query(
                OFS.numOF,
                OFS.Modele,
                OFS.Quantite,
                OFS.Pointure,
                OFS.Coloris,
                OFS.dateCreation,
                OFS.observation,
                OFS.colisNonEmb,
                OFS.nbre,
                OFS.magasin,
                OFS.inventaire,
                OFS.DF,
                OFS.export,
                # Dates pour Coupe
                coupe.dateLancement_of_chaine.label("entre_Coupe"),
                coupe.dateFin.label("sortie_Coupe"),

                # Dates pour Piqure
                piqure.idChaine.label("atelierPiqure"),
                piqure.dateLancement_of_chaine.label("entre_Piqure"),
                piqure.dateFin.label("sortie_Piqure"),

                # Dates pour Montage
                montage.dateLancement_of_chaine.label("entre_Montage"),
                montage.dateFin.label("sortie_Montage"),
            )
            .join(coupe, (OFS.numOF == coupe.numCommandeOF) & (coupe.idChaine == 'coupe'), isouter=True)
            .join(piqure, (OFS.numOF == piqure.numCommandeOF) & (piqure.idChaine.like('piqure%')), isouter=True)
            .join(montage, (OFS.numOF == montage.numCommandeOF) & (montage.idChaine.like('montage%')), isouter=True)
            .filter(OFS.Modele == modele)
            .group_by(OFS.numOF)
        )

        return query.all()

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
    def delete_chaine(self):
        db.session.delete(self)
        db.session.commit()
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

    @classmethod
    def get_nb_of_termine_par_modele(cls, modele_donne, num):
        num_str = str(num)

        subquery = (
            db.session.query(
                OFS.numOF.label("numOF"),
                OFS.Modele.label("Modele"),
                func.sum(
                    case(
                        (OFSChaine.etat != "termine", 1),
                        else_=0
                    )
                ).label("non_termine_count")
            )
            .join(OFSChaine, OFS.numOF == OFSChaine.numCommandeOF)
            .group_by(OFS.numOF, OFS.Modele)
            .subquery()
        )

        # on cast subquery.c.numOF ici en string
        numof_str = cast(subquery.c.numOF, String)
        length_numof = func.length(numof_str)

        substring_cond = case(
            (length_numof == 6, func.substr(numof_str, 2)),
            (length_numof == 8, func.substr(numof_str, 4)),
            else_=func.substr(numof_str, 2)
        )

        query = (
            db.session.query(
                subquery.c.numOF,
                func.count(subquery.c.numOF.distinct()).label("nb_termine")
            )
            .filter(subquery.c.non_termine_count == 0)
            .filter(subquery.c.Modele == modele_donne)
            .filter(substring_cond.like(f"%{num_str}%"))  # ici c'est bon maintenant
            .group_by(subquery.c.Modele)
        )

        return query.all()

    @classmethod
    def getofsJOINOuvriersby_modele_num_chaine(cls,modele_donne,num,chaine):
        custom_order = case(
            (func.substr(OFSChaine.idChaine, 1, 1) == 'c', 0),
            (func.substr(OFSChaine.idChaine, 1, 1) == 'q', 1),
            (func.substr(OFSChaine.idChaine, 1, 1) == 'm', 2),
            else_=3
        )
        # Conversion numOF en string
        num_str = str(num)
        numof_str = cast(OFSChaine.numCommandeOF, String)
        length_numof = func.length(numof_str)

        # Calcul dynamique de la position
        start_pos = case(
            (length_numof == 6, 2),
            else_=4
        )

        substring_cond = case(
            (length_numof == 6, func.substr(numof_str, 2)),
            (length_numof == 8, func.substr(numof_str, 4)),
            else_=func.substr(numof_str, 2)  # fallback
        )
        query = db.session.query(
            OFSChaine.numCommandeOF,
            OFSChaine.dateLancement_of_chaine,
            OFSChaine.dateFin,
            OFSChaine.etat,
            OFS.Quantite,
            OFS.Pointure,
            OFS.SAIS,
            OFS.dateCreation,
            func.coalesce(
                func.group_concat(ouvrier_chaine_ofs.matOuvrier.op('SEPARATOR')(', ')),
                "-"
            ).label("ouvriers")
        ).join(
            OFS, OFS.numOF == OFSChaine.numCommandeOF
        ).join(
            ouvrier_chaine_ofs, OFSChaine.numCommandeOF == ouvrier_chaine_ofs.numCommandeOF,
            isouter=True  # important si tu veux inclure les cas sans ouvriers
        ).filter(
            OFS.Modele == modele_donne,
            substring_cond.like(f"%{num_str}%"),
            OFSChaine.idChaine == chaine

        ).group_by(
            OFSChaine.numCommandeOF
        )
        return query.all()

    #afficher les ofs dans la table ofschaines par chaine et le nombres des of encours,termine et en attente
    @classmethod
    def get_all_ofchaines_by_modeleAndnumOf(cls, modele_donne, num):
        custom_order = case(
            (func.substr(OFSChaine.idChaine, 1, 1) == 'c', 0),
            (func.substr(OFSChaine.idChaine, 1, 1) == 'p', 1),
            (func.substr(OFSChaine.idChaine, 1, 1) == 'm', 2),
            else_=3
        )
        num_str = str(num)

        # Convertir numOF en chaîne de caractères
        numof_str = cast(OFS.numOF, String)

        # Longueur du numOF
        length_numof = func.length(numof_str)

        # Extraction conditionnelle selon la longueur
        substring_cond = case(
            (length_numof == 6, func.substr(numof_str, 2)),
            (length_numof == 8, func.substr(numof_str, 4)),
            else_=func.substr(numof_str, 2)  # fallback
        )

        query = (
            db.session.query(
                OFSChaine.idChaine,
                func.sum(case((OFSChaine.etat == "enAttente", 1), else_=0)).label("nb_en_attente"),
                func.sum(case((OFSChaine.etat == "enCours", 1), else_=0)).label("nb_en_cours"),
                func.sum(case((OFSChaine.etat == "termine", 1), else_=0)).label("nb_termine")
            )
            .join(OFS, OFS.numOF == OFSChaine.numCommandeOF)
            .filter(OFS.Modele == modele_donne)
            .filter(substring_cond.like(f"%{num_str}%"))  # filtre dynamique
            .group_by(OFSChaine.idChaine)
            .order_by(custom_order,OFSChaine.idChaine.asc())
        )

        return query.all()

    @classmethod
    def get_inProgress_ofs_by_modele(cls, modele, num):
        num_str = str(num)
        numof_str = cast(OFS.numOF, String)
        length_numof = func.length(numof_str)

        substring_cond = case(
            (length_numof == 6, func.substr(numof_str, 2)),
            (length_numof == 8, func.substr(numof_str, 4)),
            else_=func.substr(numof_str, 2)
        )

        # Sous-requête : compter les états par OF
        subquery = (
            db.session.query(
                OFSChaine.numCommandeOF.label("of_num"),
                func.sum(case((OFSChaine.etat == "enCours", 1), else_=0)).label("nb_encours"),
                func.sum(case((OFSChaine.etat == "termine", 1), else_=0)).label("nb_termine"),
                func.sum(case((OFSChaine.etat == "enAttente", 1), else_=0)).label("nb_attente"),
            )
            .group_by(OFSChaine.numCommandeOF)
            .subquery()
        )

        # Requête principale : sélectionner les OFs "en cours"
        query = (
            db.session.query(
                OFS.Modele,
                func.count(func.distinct(OFS.numOF)).label("nb_inProgress")
            )
            .join(subquery, subquery.c.of_num == OFS.numOF)
            .filter(
                OFS.Modele == modele,
                substring_cond.like(f"%{num_str}%"),
                (
                        (subquery.c.nb_encours > 0) |
                        ((subquery.c.nb_termine > 0) & (subquery.c.nb_attente > 0))
                )
            )
            .group_by(OFS.Modele)
        )

        return query.all()

    @classmethod
    def get_waiting_ofs(cls,modele, num):
        query = (
            db.session.query(
                OFS.Modele,
                func.count(distinct(OFSChaine.numCommandeOF)).label('nb_enAttente')
            )
            .join(OFSChaine, OFS.numOF == OFSChaine.numCommandeOF)
            .filter(
                OFS.Modele == modele,
                func.substr(cast(OFS.numOF, String), 2).like(f"{num}%"),
                OFSChaine.idChaine == 'coupe',
                OFSChaine.etat == 'enAttente'
            )
            .group_by(OFS.Modele)
        )
        return query.all()


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

class Planification(db.Model):
    __tablename__ = 'planification'
    id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    modele=db.Column(db.String(100))
    chaine=db.Column(db.String(20), db.ForeignKey('type_chaine.id'), nullable=False)
    regimeHoraire=db.Column(db.Integer)
    horaireLundi=db.Column(db.Float)
    nbPaireLundi=db.Column(db.Integer)
    horaireMardi = db.Column(db.Float)
    nbPaireMardi = db.Column(db.Integer)
    horaireMercredi = db.Column(db.Float)
    nbPaireMercredi = db.Column(db.Integer)
    horaireJeudi = db.Column(db.Float)
    nbPaireJeudi = db.Column(db.Integer)
    horaireVendredi = db.Column(db.Float)
    nbPaireVendredi = db.Column(db.Integer)
    horaireSamedi=db.Column(db.Float)
    nbPaireSamedi=db.Column(db.Integer)

    def save_planification(self):
        db.session.add(self)
        db.session.commit()
    def update_planification(self, new_data):
        self.horaireLundi = new_data.horaireLundi
        self.nbPaireLundi = new_data.nbPaireLundi
        self.horaireMardi = new_data.horaireMardi
        self.nbPaireMardi = new_data.nbPaireMardi
        self.horaireMercredi = new_data.horaireMercredi
        self.nbPaireMercredi = new_data.nbPaireMercredi
        self.horaireJeudi = new_data.horaireJeudi
        self.nbPaireJeudi = new_data.nbPaireJeudi
        self.horaireVendredi = new_data.horaireVendredi
        self.nbPaireVendredi = new_data.nbPaireVendredi
        self.horaireSamedi = new_data.horaireSamedi
        self.nbPaireSamedi = new_data.nbPaireSamedi

        db.session.commit()

    @classmethod
    def get_planification_by_modele_regimeHor_chaine(cls, chaine, modele, regimeHoraire):
        print(chaine, modele, regimeHoraire)
        return cls.query.filter_by(
            chaine=chaine,
            modele=modele,
            regimeHoraire=regimeHoraire
        ).first()

    @classmethod
    def get_planification_by_modele_chaine(cls, chaine, modele):
        print(chaine, modele)
        return cls.query.filter_by(
            chaine=chaine,
            modele=modele,
        ).all()
class CodeModeles(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = 'code_modeles'
    nom_modele=db.Column(db.String(255), primary_key=True)
    code=db.Column(db.String(50),)

    @classmethod
    def get_all_codemodeles(cls):
        return cls.query.all()


