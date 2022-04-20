from flask import Flask, jsonify, request, make_response
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

from project.models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/flask_db'
app.config['SECRET_KEY'] = 'super secret key'

db.init_app(app)
Migrate(app, db)
bcrypt = Bcrypt(app)

from project import routes
