import jwt
from flask_httpauth import HTTPTokenAuth


jwt_auth = HTTPTokenAuth(scheme="jwt")


@jwt_auth.verify_token
def verify_token(token):
    pass
