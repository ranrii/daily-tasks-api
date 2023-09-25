from flask import abort
from sqlalchemy import select

from app import db
from app.middleware.token import decode_token
from app.models.user import User


def get_user(user_id):
    user = db.session.scalar(select(User).where(User.id == user_id))
    if user is None:
        return abort(404, "user not found")
    return user
