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
    dateCreation = fields.Date()
    etat = fields.String()
    parcours = fields.String()
    regimeHoraire=fields.Integer()

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
class GetofsGroupByidChaineSchema(Schema):
    __tablename__ = 'ofs_chaine'
    idChaine=fields.String()
    dateLancement_of_chaine=fields.Date()
    dateFin=fields.Date()
    etat=fields.String()
    matOuvrier=fields.Integer()
    nb_en_attente=fields.Integer()
    nb_en_cours=fields.Integer()
    nb_termine=fields.Integer()

class GetofsByidChaineSchema(Schema):
    __tablename__ = 'ofs_chaine'
    numCommandeOF=fields.Integer()
    dateLancement_of_chaine=fields.Date()
    dateFin=fields.Date()
    etat=fields.String()
    ouvriers=fields.String()
    Quantite=fields.Integer()
    Pointure=fields.Integer()
    SAIS=fields.String()
    dateCreation=fields.Date()
class get_all_ofs_by_modelesSchema(Schema):
    __tablename__ = 'ofs'
    numOF = fields.Integer()
    Modele = fields.String()
    Quantite = fields.Integer()
    Pointure = fields.String()
    Coloris = fields.String()
    observation = fields.String()
    inventaire = fields.String()
    magasin = fields.String()
    nbre = fields.Integer()
    colisNonEmb = fields.Integer()
    DF = fields.Date()
    export=fields.String()
    dateCreation=fields.Date()
    # Coupe
    entre_Coupe = fields.Date(allow_none=True)
    sortie_Coupe = fields.Date(allow_none=True)

    # Piqure
    atelierPiqure = fields.String(allow_none=True)
    entre_Piqure = fields.Date(allow_none=True)
    sortie_Piqure = fields.Date(allow_none=True)

    # Montage
    entre_Montage = fields.Date(allow_none=True)
    sortie_Montage = fields.Date(allow_none=True)
class ModelesSchema(Schema):
    __tablename__ = 'code_modeles'
    nom_modele=fields.String()
class PlanificationSchema(Schema):
    __tablename__ = 'planifications'
    id =fields.Integer()
    modele = fields.String()
    chaine = fields.String()
    regimeHoraire = fields.Integer()
    horaireLundi = fields.Float()
    nbPaireLundi = fields.Integer()
    horaireMardi = fields.Float()
    nbPaireMardi = fields.Integer()
    horaireMercredi = fields.Float()
    nbPaireMercredi = fields.Integer()
    horaireJeudi = fields.Float()
    nbPaireJeudi = fields.Integer()
    horaireVendredi = fields.Float()
    nbPaireVendredi = fields.Integer()
    horaireSamedi = fields.Float()
    nbPaireSamedi = fields.Integer()
class PlanificationChaineModeleSchema(Schema):
    __tablename__ = 'planifications'
    id =fields.Integer()
    modele = fields.String()
    chaine = fields.String()
    regimeHoraire = fields.Integer()
    horaireLundi = fields.Float()
    nbPaireLundi = fields.Integer()
    horaireMardi = fields.Float()
    nbPaireMardi = fields.Integer()
    horaireMercredi = fields.Float()
    nbPaireMercredi = fields.Integer()
    horaireJeudi = fields.Float()
    nbPaireJeudi = fields.Integer()
    horaireVendredi = fields.Float()
    nbPaireVendredi = fields.Integer()
    horaireSamedi = fields.Float()
    nbPaireSamedi = fields.Integer()