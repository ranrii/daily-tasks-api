import time

import jwt
from flask import request, abort, current_app
from flask_httpauth import HTTPTokenAuth
from jwt import ExpiredSignatureError, DecodeError, InvalidSignatureError

from app import db

from app.models.user import User

jwt_auth = HTTPTokenAuth(scheme="Bearer")


@jwt_auth.verify_token
def verify_token(token):
    try:
        decoded = jwt.decode(
            token,
            current_app.secret_key,
            algorithms=["HS256"],
            options={
                "require": ["iss", "sub", "aud", "iat", "exp"],
                "verify_signature": True,
                "verify_iss": True,
                "verify_exp": True
            },
            issuer="ranrii",
            leeway=300
        )
    except InvalidSignatureError:
        return abort(401, "invalid token")
    except DecodeError:
        return abort(401, "invalid token")
    except ExpiredSignatureError:
        return abort(401, "token expired")
    user = db.session.execute(
        db.select(User).where(User.id == decoded["sub"] and User.email == decoded["aud"])).one_or_none()
    if user is None:
        return abort(401, "no user associated with this token")
    return True


def issue_token(user, length: int):
    payload = {
        "iss": "ranrii",
        "sub": user.id,
        "aud": user.email,
        "iat": time.time(),
        "exp": time.time()+length
    }
    return jwt.encode(payload=payload, key=current_app.secret_key, algorithm="HS256")
