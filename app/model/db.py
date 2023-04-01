import base64
from functools import wraps

import jwt
from flask import request, jsonify
from pymongo import MongoClient
import ssl

from app.modules.apimodule.userservice import UserService


class ConnectDB:
    def __init__(self):
        self.connection = None
        self.collection = None

    @staticmethod
    def connect_db():
        password = b'cm9vdA=='
        base64.b64decode(password).decode('utf-8')
        connection = MongoClient(
            "mongodb+srv://drttrimark:drttrimark31012023@drttrimark.ylmqj.mongodb.net/?retryWrites=true&w=majority")
        #connection = MongoClient(
        #    "mongodb+srv://root:root@cluster0.jinb4pq.mongodb.net/?retryWrites=true&w=majority")
        return connection

    @staticmethod
    def close_db(client):
        client.close()


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'A valid token is missing'})
        try:
            data = jwt.decode(token, "fmaihds76sa786d98siaohdn", algorithms=["HS256"])
            current_user = UserService.get_user_by_id(data["public_id"])
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)

    return decorator