from blacklist import BLACKLIST
from flask_jwt_extended.utils import get_jwt_identity, get_raw_jwt
from flask_jwt_extended.view_decorators import jwt_required
from models.user import UserModel
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_refresh_token_required

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This field cannot be left blank!"
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be left blank!"
                          )


class UserRegister(Resource):

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "User with that username already exists."}, 400

        user = UserModel(**data)

        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id):
        """
        Get user
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {
                'message': 'User not found'
            }, 404
        return user.json()

    @classmethod
    def delete(cls, user_id):
        """
        delete User
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {
                'message': 'User not found'
            }, 404
        user.delete_from_db()
        return {
            'message': 'User deleted'
        }, 200


class UserLogin(Resource):
    """
    Dang nhap nguoi dung
    """
    @classmethod
    def post(cls):
        """
        Kiem tra dang nhap nguoi dung
        """
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {
            'message': 'Invalid credentials'
        }, 401

class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti'] # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": "User <id={}> successfully logged out.".format(user_id)}, 200

class RefreshToken(Resource):
    """
    Lam moi token het han
    """
    @jwt_refresh_token_required
    def post(self):
        """
        Refresh Token
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        new_refresh_token = create_refresh_token(identity=current_user)
        return {
            'access_token': new_token,
            'refresh_token': new_refresh_token
        },200