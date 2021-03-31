from datetime import datetime
from time import sleep

from flask import request, make_response, Blueprint, current_app
from marshmallow import ValidationError, EXCLUDE
from sqlalchemy.exc import SQLAlchemyError

from models import WalletSchema, UserSchema, Wallet, User, TransactionLog
from config import Config
from server import db

wallet_bp = Blueprint('wallet_bp', __name__)
USER_SCHEMA = UserSchema()
WALLET_SCHEMA = WalletSchema()


@wallet_bp.route('/', methods=['POST'])
def create_wallet():
    try:
        user = USER_SCHEMA.load(request.json, unknown=EXCLUDE)
        wallet = WALLET_SCHEMA.load(request.json, unknown=EXCLUDE)
    except ValidationError as e:
        return make_response({'errors': [e.messages]}, 400, {'Content-Type': 'application/json'})

    result = db.session.query(Wallet, User).filter(User.phone == user.phone).filter(Wallet.user_id == User.id)\
        .one_or_none()

    if result:
        current_app.logger.debug("Wallet already exists for user : {phone}".format(phone=user.phone))
        return make_response({'errors': ["Wallet already exists for user : {phone}".format(phone=user.phone)]},
                             400, {'Content-Type': 'application/json'})

    try:
        user_exists = User.query.filter(User.phone == user.phone).one_or_none()
        if user_exists is None:
            db.session.add(user)
            db.session.commit()
        else:
            user = user_exists

        wallet.user_id = user.id
        db.session.add(wallet)
        db.session.commit()

        transaction_log = TransactionLog(wallet_id=wallet.id, amount=wallet.balance)
        db.session.add(transaction_log)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return make_response({'errors': e.orig.args}, 500, {'Content-Type': 'application/json'})

    data = {**USER_SCHEMA.dump(user), **WALLET_SCHEMA.dump(wallet)}
    return make_response(data, 201, {'Content-Type': 'application/json'})


@wallet_bp.route('/add', methods=['PUT'])
def credit_wallet():
    try:
        user = USER_SCHEMA.load(request.json, unknown=EXCLUDE)
        amount = float(request.json.get('amount'))
    except ValidationError as e:
        print(e.messages)
        return make_response({'errors': [e.messages]}, 400, {'Content-Type': 'application/json'})
    except ValueError as e:
        return make_response({'errors': e.args}, 400, {'Content-Type': 'application/json'})

    db.session.begin_nested()    # Have to keep it here because we want Read and Write/Update in one transaction.
    result = db.session.query(Wallet, User).filter(User.phone == user.phone).filter(Wallet.user_id == User.id)\
        .one_or_none()
    if result is None:
        return make_response({'errors': ["Wallet not found for user : {user}".format(user=user.phone)]},
                             404, {'Content-Type': 'application/json'})

    err_msgs = None
    for i in range(Config.RETRIES_ON_DB_LOCK):
        try:
            wallet, user = result     # Values in result are getting updated after commit of other transaction. So, no need to query again.
            print(str(amount) + "--------" + str(result))
            transaction_log = TransactionLog(wallet_id=wallet.id, amount=amount)
            wallet.balance += amount
            db.session.add(transaction_log)
            db.session.commit()

            data = {**USER_SCHEMA.dump(user), **WALLET_SCHEMA.dump(wallet)}
            return make_response(data, 200, {'Content-Type': 'application/json'})
        except SQLAlchemyError as e:
            db.session.rollback()
            err_msgs = e.orig.args
            sleep(1)

    return make_response({'errors': err_msgs}, 500, {'Content-Type': 'application/json'})


@wallet_bp.route('/deduct', methods=['PUT'])
def debit_wallet():
    try:
        user = USER_SCHEMA.load(request.json, unknown=EXCLUDE)
        amount = float(request.json.get('amount'))
    except ValidationError as e:
        print(e.messages)
        return make_response({'errors': [e.messages]}, 400, {'Content-Type': 'application/json'})
    except ValueError as e:
        return make_response({'errors': e.args}, 400, {'Content-Type': 'application/json'})

    db.session.begin_nested()
    result = db.session.query(Wallet, User).filter(User.phone == user.phone).filter(Wallet.user_id == User.id)\
        .one_or_none()
    if result is None:
        return make_response({'errors': ["Wallet not found for user : {user}".format(user=user.phone)]},
                             404, {'Content-Type': 'application/json'})

    err_msgs = None
    for i in range(Config.RETRIES_ON_DB_LOCK):
        wallet, user = result
        print(str(amount) + "--------" + str(result))
        wallet.balance -= amount
        if wallet.balance < Config.MIN_BAL:
            return make_response({'errors': ["Insufficient balance for user : {user}".format(user=user.phone)]}, 400,
                                 {'Content-Type': 'application/json'})

        try:
            transaction_log = TransactionLog(wallet_id=wallet.id, amount=-amount)
            db.session.add(transaction_log)
            db.session.commit()

            data = {**USER_SCHEMA.dump(user), **WALLET_SCHEMA.dump(wallet)}
            return make_response(data, 200, {'Content-Type': 'application/json'})
        except SQLAlchemyError as e:
            db.session.rollback()
            err_msgs = e.orig.args
            sleep(1)

    return make_response({'errors': err_msgs}, 500, {'Content-Type': 'application/json'})


@wallet_bp.route('/get_balance', methods=['POST'])
def get_balance():
    try:
        user = USER_SCHEMA.load(request.json)
    except ValidationError as e:
        return make_response({'errors': e.messages}, 400, {'Content-Type': 'application/json'})

    result = db.session.query(Wallet, User).filter(User.phone == user.phone).filter(Wallet.user_id == User.id)\
        .one_or_none()
    if result:
        wallet, user = result
        data = {**USER_SCHEMA.dump(user), **WALLET_SCHEMA.dump(wallet)}
        return make_response(data, 200, {'Content-Type': 'application/json'})
    else:
        return make_response({'errors': ["Wallet not found for user : {user}".format(user=user.phone)]},
                             404, {'Content-Type': 'application/json'})

