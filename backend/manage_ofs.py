from flask import Blueprint,jsonify,request
from models import User
from schemas import  OFSSchema
from flask_jwt_extended import jwt_required, get_jwt, current_user
from models import OFS
manage_ofs_bp=Blueprint('manage_ofs', __name__)


@manage_ofs_bp.post("/addOfs")
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
@manage_ofs_bp.get("/getAllLatestOfs")
@jwt_required()
def getAllLatestOfs():
    if current_user.role == "production":
        ofs=OFS.get_all_latest_ofs()
        ofs_result = OFSSchema().dump(ofs, many=True)
        return jsonify({
            "users":ofs_result,
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
@manage_ofs_bp.delete("/deleteUser")
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
@manage_ofs_bp.put("/updateUser")
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


@manage_ofs_bp.get("/getUserById")
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

@manage_ofs_bp.put("/updateAuthorization")
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


