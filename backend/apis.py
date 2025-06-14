import os
import sys

from flask import Flask, request
import mysql.connector
from flask.cli import load_dotenv
from flask_migrate import Migrate
from extension import db,jwt
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

from models import *
@app.route("/login",methods=["GET"])
def login():
    try:
        data = request.get_json()
        # query="select * from users where username = %s and pwd=%s"
        # cursor.execute(query, (data['username'], data['password']))
        # user=cursor.fetchone()
        # cursor.close()
        # if user:
        #   return user
        # else:
        #     return jsonify({'message': 'Invalid credentials'}), 401
    except mysql.connector.Error as err:
        print(err)


if __name__ == "__main__":
    app.run(debug=True)


