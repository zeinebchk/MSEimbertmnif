from flask import Blueprint,jsonify,request
from models import TypeChaine
from schemas import ChaineSchema
from flask_jwt_extended import jwt_required, get_jwt, current_user

manage_chaine_roles_bp=Blueprint('manage_roles_chaine', __name__)


@manage_chaine_roles_bp.post("/addchaineOrRole")
@jwt_required()
def addChaineOrRole():
    if current_user.role == "userManager":
        data=request.get_json()
        role=TypeChaine.get_type_chaine_byID(id=data.get("id"))
        if role is not None:
            return jsonify({"error": "role already exists"},409)
        else:

            new_role=TypeChaine(
                id=data.get("id"),
              )

            new_role.save_chaine()
            return jsonify({"message": "chaine or role  added successfully"},200)
    return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"},401)

@manage_chaine_roles_bp.get("/getAllRoles")
@jwt_required()
def getAllRoles():
    if current_user.role in ["userManager","production"]:
       roles=TypeChaine.get_all_chaines()
       roles_result = ChaineSchema().dump(roles, many=True)
       return jsonify({
            "roles":roles_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    },401),


@manage_chaine_roles_bp.get("/getChaineOrRoleByID")
@jwt_required()
def getRoleById():
    if current_user.role == "userManager":
        data = request.get_json()
        id = data.get("id")
        role = TypeChaine.get_type_chaine_byID(id=id)
        if role is not None:
            return jsonify({
                "user": ChaineSchema.dump(role),
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)




