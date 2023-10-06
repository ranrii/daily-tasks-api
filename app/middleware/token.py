import time

import jwt
from flask import current_app, abort
from jwt import InvalidSignatureError, DecodeError, ExpiredSignatureError, InvalidAlgorithmError, InvalidTokenError

from app.models.user import User


def decode_token(token, token_type="access", refresh=False):
    if token_type == "refresh":
        secret_key = "REFRESH_TOKEN_SECRET"
    elif token_type == "reset_pw":
        secret_key = "RESET_PASSWORD_SECRET"
    else:
        secret_key = "ACCESS_TOKEN_SECRET"
    if current_app.testing:
        refresh = current_app.config["NO_EXP_TOKEN"]
    try:
        decoded = jwt.decode(
            token,
            current_app.config[secret_key],
            algorithms=["HS256"],
            options={
                "require": ["iss", "sub", "aud", "iat", "exp"],
                "verify_signature": True,
                "verify_iss": True,
                "verify_exp": not refresh,
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
    except InvalidTokenError:
        return abort(401, "invalid token")
    if refresh or token_type == "refresh":
        del decoded["exp"], decoded["iat"]
    return decoded


def issue_token(user: User, length: int, token_type="access"):
    secret_key = "ACCESS_TOKEN_SECRET"
    if token_type == "refresh":
        secret_key = "REFRESH_TOKEN_SECRET"
    elif token_type == "reset_pw":
        secret_key = "RESET_PASSWORD_SECRET"

    payload = {
        "iss": "ranrii",
        "sub": user.id,
        "aud": user.email,
        "iat": time.time(),
        "exp": time.time()+length
    }
    return jwt.encode(payload=payload, key=current_app.config[secret_key], algorithm="HS256")
