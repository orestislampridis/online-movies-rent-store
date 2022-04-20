from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from project.config import DEV_DB, PROD_DB, SECRET_KEY
from project.models import db

app = Flask(__name__)

if os.environ.get('DEBUG') == '1':
    app.config['SQLALCHEMY_DATABASE_URI'] = DEV_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = PROD_DB

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

from project import routes
