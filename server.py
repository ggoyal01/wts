import os

from flask import Flask
from marshmallow import INCLUDE, EXCLUDE

from config import Config
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from resources.v1.wallet import wallet_bp
app.register_blueprint(wallet_bp, url_prefix='/v1/wallet')

if not os.path.isfile(Config.SQLALCHEMY_DATABASE_URI.split('/', 3)[3]):
    db.create_all()
    db.session.commit()
