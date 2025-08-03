from flask import request
from flask_restful import Resource

from ..extensions import db
from ..models import User


class Register(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(email=data.get('email')).first():
            return {'message': 'Email already registered'}, 400
        user = User(email=data['email'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User registered'}, 201


class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()
        if user and user.check_password(data.get('password')):
            token = user.create_token()
            return {'access_token': token}, 200
        return {'message': 'Invalid credentials'}, 401
