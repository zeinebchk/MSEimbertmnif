from flask import Blueprint,jsonify,request
from models import User
manageusers_bp=Blueprint('manage_users', __name__)

@manageusers_bp.post("/addUser")
def addUser():
    data=request.get_json()
    user=User.get_user_by_username(username=data.get("username"))
    if user is not None:
        return jsonify({"error": "user already exists"})
    else:
        new_user=User(
            username=data.get("username"),
            role=data.get("role"),)
        new_user.generate_password(password=data.get("password"))
        new_user.save_user()
        return jsonify({"message": "User added successfully"})
@manageusers_bp.post("/getUsers")
def getUsers():
    users=User.get_all_users()
    if users.count()!=0:
        return jsonify({"error": "user already exists"},200)
    else:
        return jsonify({"message": "User added successfully"})



