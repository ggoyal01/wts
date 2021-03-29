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

from models import UserSchema, WalletSchema, Wallet
user = UserSchema().load(data={"user": {"phone": "9604234840"}})
print(type(user))
print(user)
print(float(Config.MIN_BAL))
wallet = WalletSchema(unknown=EXCLUDE).load({"amount": 500.99, "x": 1})
print(WalletSchema(unknown=EXCLUDE).load({"amount": 500.99, "x": 1}))
print(wallet)
# wallet = Wallet(id=1, user_id=1, balance=499.00)
# print({**WalletSchema().dump(wallet), **UserSchema().dump(user)})
# db.session.add(user)
# print(user.id)
# db.session.commit()
# print(user.id)
