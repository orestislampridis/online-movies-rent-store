from flask import Flask
from flask_bcrypt import Bcrypt
import os

from flask_sqlalchemy import SQLAlchemy
from video_club.config import DEV_DB, PROD_DB, SECRET_KEY

app = Flask(__name__)

if os.environ.get('DEBUG') == '1':
    app.config['SQLALCHEMY_DATABASE_URI'] = DEV_DB
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = PROD_DB

app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

db.init_app(app)
bcrypt = Bcrypt(app)

from video_club import routes
