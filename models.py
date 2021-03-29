from datetime import datetime

from marshmallow import Schema, fields, validate, post_load, post_dump, pre_load

from config import Config
from server import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), index=True, unique=True, nullable=False)

    def __repr__(self):
        return "<id : {id}, Phone : {phone}>".format(id=self.id, phone=self.phone)


class UserSchema(Schema):
    phone = fields.String(validate=validate.Regexp(regex="^[789]\\d{9}$", error="Invalid phone number."))

    @pre_load()
    def unwrap_envelope(self, data, **kwargs):
        key = "user"
        return data[key]

    @post_dump()
    def wrap_with_envelope(self, data, **kwargs):
        key = "user"
        return {key: data}

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    balance = db.Column(db.Float)

    def __repr__(self):
        return "<id : {id}, User Id: {user}, balance : {bal}>".format(id=self.id, user=self.user_id, bal=self.balance)


class WalletSchema(Schema):
    user = fields.Nested(UserSchema)
    balance = fields.Float(validate=validate.Range(min=float(Config.MIN_BAL),
                                                   error="Amount must be grater than {min_bal}".format(min_bal=
                                                                                                       Config.MIN_BAL)))

    @pre_load()
    def unwrap_envelope(self, data, **kwargs):
        return {"balance": data["amount"]}

    @post_load
    def make_user(self, data, **kwargs):
        return Wallet(**data)

    class Meta:
        ordered = True


class TransactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    amount = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return "<id : {id}, Wallet Id: {wallet}, amount : {amount}, timestamp : {timestamp}>".\
            format(id=self.id, wallet=self.wallet_id, amount=self.amount, timestamp=self.timestamp)
