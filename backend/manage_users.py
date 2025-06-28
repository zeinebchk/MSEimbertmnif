from flask import Blueprint,jsonify,request

from models import User,Ouvriers
from schemas import UserSchema
from flask_jwt_extended import jwt_required, get_jwt, current_user

manageusers_bp=Blueprint('manage_users', __name__)


@manageusers_bp.post("/addUser")
@jwt_required()
def addUser():
    if current_user.role == "userManager":
        data=request.get_json()
        user=User.get_user_by_username(username=data.get("username"))
        if user is not None:
            return jsonify({"error": "user already exists"},409)
        else:

            new_user=User(
                username=data.get("username"),
                role=data.get("role"),
                authorized=data.get("authorized"),)
            new_user.generate_password(password=data.get("password"))

            new_user.save_user()
            return jsonify({"message": "User added successfully"},200)
    return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"},401)
@manageusers_bp.get("/getUsers")
@jwt_required()
def getUsers():
    if current_user.role == "userManager":
        users=User.get_all_users()
        users_result = UserSchema().dump(users, many=True)
        return jsonify({
            "users":users_result,
            },200)
    return jsonify({
       "message":"unauthorized"
    }),401
@manageusers_bp.delete("/deleteUser")
@jwt_required()
def deleteUser():
    if current_user.role == "userManager":
        data=request.get_json()
        id=data.get("id")
        user=User.get_user_byId(id=id)
        if user is not None:
            user.delete_user()
            return jsonify({
            "message":"user deleted successfully"
            },201)
        return jsonify({
            "message":"user doesn't exist"
        },404)
@manageusers_bp.put("/updateUser")
@jwt_required()
def updateUser():
    if current_user.role == "userManager":
        data=request.get_json()
        id=data.get("id")
        user=User.get_user_byId(id=id)
        if user is not None:
            user.update_user(data)
            return jsonify({
            "message":"user updated successfully"
            },201)
        return jsonify({
            "message":"user n'existe pas dans la base"
        },404)


@manageusers_bp.get("/getUserById")
@jwt_required()
def getUserById():
    if current_user.role == "userManager":
        data = request.get_json()
        id = data.get("id")
        user = User.get_user_byId(id=id)
        if user is not None:
            return jsonify({
                "user": user.to_dict(),
            }, 200)
        return jsonify({
            "message": "user n'existe pas dans la base"
        },404)

@manageusers_bp.put("/updateAuthorization")
@jwt_required()
def updateAuthorization():
    if current_user.role == "userManager":
        data=request.get_json()
        id=data.get("id")
        user=User.get_user_byId(id=id)
        if user is not None:
            user.update_authorization(data.get("authorized"))
            return jsonify({
            "message":"user updated successfully"
            },201)
        return jsonify({
            "message":"user n'existe pas dans la base"
        },404)





@manageusers_bp.post("/addWorker")
@jwt_required()
def addOuvrier():
    if current_user.role == "userManager":
        data=request.get_json()
        worker=Ouvriers.get_ouvrier_by_MATR(MATR=data.get("MATR"))
        if worker is not None:
            return jsonify({"error": "worker already exists"},409)
        else:

            new_worker=Ouvriers(
                MATR=data.get("MATR"),
                NOM=data.get("NOM"),
                PRENOM=data.get("PRENOM"),)

            new_worker.save_user()
            return jsonify({"message": "worker added successfully"},200)
    return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"},401)