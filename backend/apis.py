import os
import sys

from adodbapi.apibase import identity
from flask import Flask, request,jsonify
import mysql.connector
from flask.cli import load_dotenv
from flask_migrate import Migrate
from extension import db,jwt
from models import User
from flask_sqlalchemy import SQLAlchemy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from manage_users import manageusers_bp
from auth import auth_bp
app = Flask(__name__)
load_dotenv()
app.config.from_prefixed_env()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("DATABASE_URL =", os.getenv('DATABASE_URL'))
db.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(manageusers_bp,url_prefix='/manage_users')
app.register_blueprint(auth_bp,url_prefix='/auth')


#load user dans la session
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_headers,jwt_data):
    identity = jwt_data['sub']
    username=jwt_data.get('username')
    return User.query.filter_by(role=identity,username=username).one_or_none()

#add additional claims to jwt
@jwt.additional_claims_loader
def make_additional_claims(identity):
    return {"is_staff":True}


#add handlers error for jwt
@jwt.expired_token_loader
def expired_token_callback(jwt_header,jwt_data):
    return jsonify({"message": "The token has expired","error":"token expired"}), 401
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (jsonify({"message": "Invalid token","error":"invalid"}),401)
@jwt.unauthorized_loader
def missing_token_callback(error):
    return (jsonify({"message": "Request doesnt contain valid token","error":"authorization_header"}),401)

from models import *
if __name__ == "__main__":
    app.run(debug=True)


