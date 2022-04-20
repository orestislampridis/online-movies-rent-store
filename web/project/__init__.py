from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
from project.config import DEV_DB, PROD_DB
from project.models import db

app = Flask(__name__)

if os.environ.get('DEBUG') == '1':
    app.config['SQLALCHEMY_DATABASE_URI'] = DEV_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = PROD_DB

app.config['SECRET_KEY'] = 'super secret key'

db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)

from project import routes
