import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import RefreshToken, UserLogin, UserLogout, UserRegister, User
from resources.item import Item, ItemList
from resources.store import Store, StoreList

from blacklist import BLACKLIST

from db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Không lưu vào db ngay khi object bị thay đổi
app.secret_key = 'jose'
# app.config['JWT_SECRET_KEY'] = 'Lucdeptrai'
app.config['JWT_BLACKLIST_ENABLED'] = True # enable blacklist feature
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh'] # allow blacklisting for access and refresh tokens

api = Api(app)

@app.before_first_request
def create_tables():
    """
    Tạo db trước tiên khi app chạy
    """
    db.create_all()

# app.config['JWT_AUTH_URL_RULE'] = '/login'
# # config JWT to expire within half an hour
# app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=1800)
# # config JWT auth key name to be 'email' instead of default 'username'
# app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
# jwt = JWT(app, authenticate, identity) # /auth

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    """
    Add any extra data to that JWT as well
    """
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callback():
    """
    Callback function when token expired   
    """
    return jsonify({
        'description':'The token has expired.',
        'error': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'description':'Signature verification failed.',
        'error': 'invalid_token'
    }), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        'description':'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'description': 'Request does not contain an access token',
        'error': 'authorization_required'
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked',
        'error': 'token_revoked'
    }), 401

@jwt.token_in_blacklist_loader
def check_if_token_in_backlist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST

api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>') 
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(RefreshToken, '/refresh')

if __name__ == "__main__":
    db.init_app(app)
    app.run(host="localhost", port=5000, debug=True)
