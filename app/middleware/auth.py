import datetime
from functools import wraps

import pytz
from flask import request, abort, current_app
from sqlalchemy import select, and_

from app import db
from app.middleware.token import decode_token
from app.models.user import User


def jwt_required(roles=None):
    def wrap(function):
        @wraps(function)
        def decorated(*args, **kwargs):

            current_user = get_current_user()
            debug_msg = f" username: {current_user.username}" if current_app.debug else ""
            if current_user.login_at is None:
                return abort(403, "user is logged out, please login" + debug_msg)
            elif (current_user.login_at.replace(tzinfo=pytz.utc)
                  - datetime.timedelta(days=1) >= datetime.datetime.now(pytz.UTC)):

                current_user.login_at = None
                db.session.commit()
                return abort(403, "session expired, please login" + debug_msg)

            if roles is not None and current_user.role not in roles:
                return abort(403)
            return function(current_user, *args, **kwargs)
        return decorated
    return wrap


def get_current_user():
    token = request.headers.get("token")
    debug_msg = ": no token received" if current_app.debug else ""
    if token is None:
        return abort(401, "Unauthorized" + debug_msg)
    decoded = decode_token(token, token_type="access")
    current_user = db.session.execute(select(User).where(and_(
        User.id == decoded["sub"], User.email == decoded["aud"]))).scalar_one_or_none()
    if current_user is None:
        return abort(404, "user not found")
    if current_user.is_block:
        return abort(403)
    return current_user
