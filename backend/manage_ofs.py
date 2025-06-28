from flask import Blueprint,jsonify,request
from schemas import OFSSchema, GetOfsForUpdate,GetOfsByModele
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import OFS,OFSChaine
manage_ofs_bp=Blueprint('manage_ofs', __name__)



@manage_ofs_bp.post("/addOfs_chaines")
@jwt_required()
def addofschaine():
    if current_user.role == "production":
        data=request.get_json()
        print(data)

        for of in data:
            ofchaine=OFSChaine.get_ofs_chaine_by_numOF(of["numCommandeOF"],of["idchaine"])
            print(ofchaine)
            if ofchaine is None:
                ofch=OFSChaine(
                    idChaine=of["idchaine"],
                    numCommandeOF=of["numCommandeOF"],
                    dateLancement_of_chaine=None,
                    dateFin = None,
                    etat="enAttente"
                )
                ofch.save_chaine_of()
                of=OFS.get_of_by_numOF(of["numCommandeOF"])
                if of is not None:
                    of.updateEtatAndDateLancement()
            else:
                return jsonify({"message": "les ofs existe déja"}, 409)

        return jsonify({"message": "ofs_chaines added successfully"}, 200)
    else:
        return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"}, 401)

    #     else:
    #
    #         new_user=User(
    #             username=data.get("username"),
    #             role=data.get("role"),
    #             authorized=data.get("authorized"),)
    #         new_user.generate_password(password=data.get("password"))
    #
    #         new_user.save_user()
    #         return jsonify({"message": "User added successfully"},200)
    # return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"},401)




@manage_ofs_bp.get("/getAllLatestOfs")
@jwt_required()
def getAllLatestOfs():
    if current_user.role == "production":
        ofs=OFS.get_all_nonlance_ofs()
        ofs_result = OFSSchema(many=True).dump(ofs)
        return jsonify({
            "ofs":ofs_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401)
@manage_ofs_bp.get("/getOfsBydate")
@jwt_required()
def getOfsBydate():
    if current_user.role == "production":
        data = request.get_json()
        date = data.get("lancementDate")
        ofs=OFS.get_ofs_by_lancementDate(date)
        ofs_result = OFSSchema().dump(ofs, many=True)
        return jsonify({
            "users":ofs_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401)

@manage_ofs_bp.put("/update_of_chaine")
@jwt_required()
def update_of_chaine():
    if current_user.role == "production":
        data=request.get_json()
        chaine_data=request.get_json().get('chaines')
        of_chaines=request.get_json().get("ofs_chaines")
        unique_ids = list(set(item["numCommandeOF"] for item in of_chaines))
        print(data)

        for numcmd in unique_ids:
            for ch in chaine_data:
                ofchaine=OFSChaine.get_ofs_chaine_by_numOF(numcmd,ch)
                if ofchaine.etat=="enAttente":
                    ofchaine.delete_of_chaine()

        for of in of_chaines:
            ofchaine = OFSChaine.get_ofs_chaine_by_numOF(of["numCommandeOF"],of["idchaine"])
            if ofchaine is None:
                ofch=OFSChaine(
                idChaine=of["idchaine"],
                numCommandeOF=of["numCommandeOF"],
                dateLancement_of_chaine=None,
                dateFin = None,
                etat="enAttente"
                )
                ofch.save_chaine_of()
        return jsonify({"message": "ofs_chaines added successfully"}, 200)
    else:
        return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"}, 401)

@manage_ofs_bp.get("/getofsChaines")
@jwt_required()
def getOFSChainesByreference():
    if current_user.role == "production":
        data = request.get_json().get('prefix')
        ofs=OFS.get_ofs_chaines(data)
        ofs_result = GetOfsForUpdate().dump(ofs, many=True)
        return jsonify({
            "ofs":ofs_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401)
@manage_ofs_bp.get("/getInprogressOFS")
@jwt_required()
def getInprogressOFS():
    if current_user.role == "production":
        prefix = request.get_json().get('prefix')
        idchaine=request.get_json().get('idchaine')
        ofs=OFS.get_inprogress_ofs(prefix,idchaine)
        ofs_result = GetOfsForUpdate().dump(ofs, many=True)
        return jsonify({
            "ofs":ofs_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401)

@manage_ofs_bp.get("/getofs_byModele")
@jwt_required()
def getofs_byModele():
    if current_user.role == "production":
        prefix = request.get_json().get('numof')
        ofs=OFS.get_ofs_by_modele(prefix)
        ofs_result = GetOfsByModele().dump(ofs, many=True)
        return jsonify({
            "ofs":ofs_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401)

