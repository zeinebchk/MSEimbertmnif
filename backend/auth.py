from datetime import timedelta

from flask import Blueprint, jsonify,request
from models import User
from flask_jwt_extended import get_jwt_identity,create_access_token, create_refresh_token, current_user, jwt_required

auth_bp=Blueprint('auth', __name__)

@auth_bp.post('/login')
def login_user():
    data=request.get_json()
    user= User.get_user_by_username(username=data.get('username'))
    print(user.check_password(data.get('password')))
    if user is None:
        return jsonify({"message": "invalid username or password"}), 400
    if not user.check_password(data.get('password')):
        return jsonify({"message": "invalid username or password"}), 400
    if user.authorized == 0:
        return jsonify({"message": "Vous n'etes pas autorisé à acceder a l'application "}),401,
    additional_claims={
        "id":user.id,
        "username":user.username,
        "role":user.role
    }
    access_token = create_access_token(identity=user.role,additional_claims=additional_claims,expires_delta=timedelta(minutes=2))
    refresh_token = create_refresh_token(identity=user.role,additional_claims=additional_claims)
    return jsonify(
        {
        "message":"logged in",
            "username":user.username,
            "role":user.role,
            "access_token":access_token,
            "refresh_token":refresh_token,
    },200)
@auth_bp.get('/refreshtoken')
@jwt_required(refresh=True)
def refresh_token():
     identity = get_jwt_identity()
     additional_claims = {
         "id": current_user.id,
         "username": current_user.username,
         "role": current_user.role
     }
     access_token = create_access_token(identity=identity, additional_claims=additional_claims,expires_delta=timedelta(minutes=2))
     return jsonify(
         {
             "access_token":access_token
         },200
     )
