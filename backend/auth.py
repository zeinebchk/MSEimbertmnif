
from flask import Blueprint, jsonify,request
from models import User
from flask_jwt_extended import create_access_token,create_refresh_token
auth_bp=Blueprint('auth', __name__)

@auth_bp.post('/login')
def login_user():
    data=request.get_json()
    user= User.get_user_by_username(username=data.get('username'))
    print(user.check_password(data.get('password')))
    if user and (user.check_password(data.get('password'))):
        print("userrrr")
        access_token = create_access_token(identity=user.role)
        refresh_token = create_refresh_token(identity=user.role)
        return jsonify(
            {
            "message":"logged in",
                "role":user.role,
                "username":user.username,
                "token":{
                    "access":access_token,
                    "refresh":refresh_token
                }
        },200)
    return jsonify(
        {
            "message":"invalid username or password",
        }
    ),400