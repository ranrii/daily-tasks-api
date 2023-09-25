import datetime

import jwt
from functools import wraps

import pytz
from flask import request, abort, current_app
from jwt import ExpiredSignatureError, DecodeError, InvalidSignatureError
from sqlalchemy import select, and_

from app import db
from app.models.user import User


def jwt_required(roles=None):
    def wrap(function):
        @wraps(function)
        def decorated(*args, **kwargs):

            current_user = get_current_user()
            if current_user.login_at is None:
                return abort(403, "user is logged out, please login")
            elif (current_user.login_at.replace(tzinfo=pytz.utc)
                  - datetime.timedelta(days=1) >= datetime.datetime.now(pytz.UTC)):

                current_user.login_at = None
                db.session.commit()
                return abort(403, "session expired, please login")

            if roles is not None and current_user.role not in roles:
                return abort(403)
            return function(current_user, *args, **kwargs)
        return decorated
    return wrap


def get_current_user():
    token = request.headers.get("token")
    if token is None:
        return abort(401, "Unauthorized")
    try:
        decoded = jwt.decode(
            token,
            current_app.config["ACCESS_TOKEN_SECRET"],
            algorithms=["HS256"],
            options={
                "require": ["iss", "sub", "aud", "iat", "exp"],
                "verify_signature": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_aud": False
            },
            issuer="ranrii",
            leeway=30
        )
    except InvalidSignatureError:
        return abort(401, "invalid token")
    except DecodeError:
        return abort(401, "invalid token")
    except ExpiredSignatureError:
        return abort(401, "token expired")
    current_user = db.session.execute(select(User).where(and_(
        User.id == decoded["sub"], User.email == decoded["aud"]))).scalar_one_or_none()
    if current_user is None:
        return abort(404, "user not found")
    if current_user.is_block:
        return abort(403)
    return current_user
