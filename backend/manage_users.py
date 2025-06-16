from flask import Blueprint,jsonify,request
from models import User
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
            return jsonify({"error": "user already exists"}),409
        else:
            new_user=User(
                username=data.get("username"),
                role=data.get("role"),)
            new_user.generate_password(password=data.get("password"))
            new_user.save_user()
            return jsonify({"message": "User added successfully"}),200
    return jsonify({"message": "Vous n'etes pas autorisé pour cette focntion"}),401
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
        username=data.get("username")
        user=User.get_user_by_username(username=username)
        if user is not None:
            user.delete_user()
        return jsonify({
            "message":"user deleted successfully"
            },201)

