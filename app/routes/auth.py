from datetime import datetime
from functools import wraps

import jwt
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash

import app
from app.extensions import db
from app.models.user import User
from utils import get_ip_addr

auth_bp = Blueprint("auth", __name__,)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict()
    if "email" not in data or "password" not in data:
        return abort(401, "invalid login details")
    try:
        email_info = validate_email(data.get("email"), check_deliverability=False)
    except EmailNotValidError as e:
        return abort(501, str(e))

    user = User.query.filter_by(email=email_info.normalized).first()
    password = data.get("password")
    if not check_password_hash(password, user.password):
        return abort(403, "Invalid login details")
    encoded_jwt = jwt.encode({"sub": user.id, "name": user.username}, algorithm="HS256")
    return jsonify({"token": encoded_jwt})


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict()
    try:
        email_info = validate_email(data.get("email"), check_deliverability=False)
    except EmailNotValidError as e:
        return abort(510, str(e))
    user = User()
    user.username = data.get("username")
    user.password = generate_password_hash(data.get("password"), method="pbkdf2", salt_length=10)
    user.first_name = data.get("first_name")
    user.last_name = data.get("last_name")
    user.email = email_info.normalized
    user.login_ip = get_ip_addr()
    user.is_block = False
    db.session.add(user)
    db.session.commit()
    return jsonify(success={"message": "successfully registered a new user"}), 200


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        header = request.headers
        token = header.get("TOKEN")
        jwt
        return function(*args, **kwargs)
    return wrapper

