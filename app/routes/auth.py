import time
from functools import wraps

import jwt
from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, request, jsonify, abort, current_app
from jwt import ExpiredSignatureError, DecodeError
from sqlalchemy import insert
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User
from app.routes import issue_token
from app.utils import get_ip_addr

auth_bp = Blueprint("auth", __name__)


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

    return jsonify({"token": issue_token(user)}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict()
    if None in data:
        return abort(400, "missing required data")
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
    user.is_admin = False
    db.session.add(user)
    db.session.commit()
    return jsonify({"token": issue_token(user)}), 200


@auth_bp.route("/refresh", methods=["GET"])
def refresh_token():
    if "token" not in request.headers:
        return abort(401, "no token provided")
    old_token = request.headers.get("token")
    decoded = jwt.decode(
        old_token,
        key=current_app.secret_key,
        algorithms="HS256",
        options={"require": ["sub", "aud", "iat"]}
    )
    if "sub" not in decoded or "aud" not in decoded or "iat" not in decoded:
        return abort(401, "invalid token")
    user = db.session.execute(db.select(User).where(User.id == decoded["sub"] and User.username == decoded["aud"])).one_or_none()
    if user is None:
        return abort(401, "no user associated with this token")
    current_ip = get_ip_addr()
    if current_ip != user.login_ip:
        return abort(401, "ip address changed, please login again")
    return jsonify({"token": issue_token(user)}), 200
