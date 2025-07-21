import os
import sys

from flask import Flask, request,jsonify
from flask.cli import load_dotenv
from flask_migrate import Migrate
from manage_planification_chaine_modele import manage_planification_modele_chaine_bp
from extension import db,jwt


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from manage_users import manageusers_bp
from auth import auth_bp
from manage_roles_chaine import manage_chaine_roles_bp
from manage_ofs import manage_ofs_bp
app = Flask(__name__)
load_dotenv()
app.config.from_prefixed_env()

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#second ebase de donnes pour recuperer les modeles
app.config['SQLALCHEMY_BINDS'] = {
    'db2': 'mysql+pymysql://omar:1234@192.168.1.210/gammes'  # base secondaire
}

print("DATABASE_URL =", os.getenv('DATABASE_URL'))
db.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(manageusers_bp,url_prefix='/manage_users')
app.register_blueprint(auth_bp,url_prefix='/auth')
app.register_blueprint(manage_chaine_roles_bp,url_prefix='/manage_chaine_roles')
app.register_blueprint(manage_planification_modele_chaine_bp,url_prefix='/manage_planification_chaine_modele')
app.register_blueprint(manage_ofs_bp,url_prefix='/manage_ofs')

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
    return jsonify({"message": "The token has expired","error":"token expired"},401)
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token","error":"invalid"},401)
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "Request doesnt contain valid token","error":"authorization_header"},401)

from models import *
if __name__ == "__main__":
    app.run(debug=True)


