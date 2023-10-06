import datetime

import jwt
import pytz
from flask import Blueprint, request, jsonify, abort, current_app
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.middleware.auth import jwt_required
from app.models.user import User, Profile
from app.middleware.token import decode_token, issue_token
from utils.connection import get_ip_addr
from utils.mail_service import send_mail, check_email
from smtplib import SMTPException
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form.to_dict()
    if None in [data.get("email"), data.get("password")]:
        return abort(401, "invalid login details")
    email = check_email(data.get("email"))
    user = db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        return abort(404, "user not found")
    password = data.get("password")
    if not check_password_hash(user.password, password):
        return abort(401, "Invalid login details")
    user.login_at = datetime.datetime.now(pytz.utc)
    db.session.commit()
    return jsonify({"user": {"id": user.id, "username": user.username},
                    "token": issue_token(user, 3600),
                    "refreshToken": issue_token(user, 259200, token_type="refresh")}), 200


@auth_bp.route("/logout", methods=["PUT"])
@jwt_required()
def logout(current_user):
    current_user.login_at = None
    db.session.commit()
    return jsonify({"success": "user has been logged out"}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict()
    if None in [data.get("username"),
                data.get("first_name"),
                data.get("last_name"),
                data.get("password"),
                data.get("email")]:
        return abort(400, "missing required data")
    email = check_email(data.get("email"))
    if db.session.scalar(select(User).where(User.email == data["email"])) is not None:
        return abort(400, "user has already registered")

    user = User()
    user_profile = Profile(user=user)
    user.username = data.get("username")
    user.password = generate_password_hash(data.get("password"), method="pbkdf2", salt_length=10)
    user.login_ip = get_ip_addr()
    user.login_at = datetime.datetime.now(pytz.utc)
    user_profile.first_name = data.get("first_name")
    user_profile.last_name = data.get("last_name")
    user.email = email
    db.session.add(user)
    db.session.add(user_profile)
    db.session.commit()
    return jsonify({"user": {"id": user.id, "username": user.username},
                    "token": issue_token(user, 3600),
                    "refreshToken": issue_token(user, 259200, token_type="refresh")}), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh_token():
    print(request.headers)
    old_token = request.headers.get("token")
    r_token = request.headers.get("refresh-token")
    print([r_token, old_token])
    if None in [r_token, old_token]:
        return abort(401, "both `token` and `refresh-token` are required")

    d_access = decode_token(token=old_token, token_type="access", refresh=True)
    d_refresh = decode_token(token=r_token, token_type="refresh")
    if d_access != d_refresh:
        return abort(403, "invalid token(s)")

    user = db.session.scalar(select(User).where(User.id == d_refresh["sub"]))
    if user is None:
        return abort(404, "user not found")

    current_ip = get_ip_addr()
    if current_ip != user.login_ip:
        user.login_at = None
        db.session.commit()
        return abort(401, "location changed, please login again")
    user.login_at = datetime.datetime.now(pytz.utc)
    db.session.commit()

    return jsonify({"user": {"id": user.id, "username": user.username},
                    "token": issue_token(user, 3600),
                    "refreshToken": issue_token(user, 86400, token_type="refresh")}), 200


# WIP or not implemented BELOW ⤵
# noinspection PyUnreachableCode
@auth_bp.route("/forget", methods=["POST"])
def forgor():
    return jsonify(error="not implemented")

    data = request.form.to_dict()
    email = check_email(data.get("email"))
    url = data.get("url")
    if None in [email, url]:
        return abort(401, "missing required data")
    user = db.session.execute(db.select(User).where(User.email == data["email"])).scalar_one_or_none()
    if user is None:
        return abort(404, "user not found")
    token = issue_token(user, 180, token_type="reset_pw")
    reset_url = f"<insert-url-to-reset-password-page-here>?reset-key={token}"
    try:
        send_mail(user, reset_url)
    except SMTPException as e:
        return jsonify(
            error={"code": 424, "message": "an error occurred while try sending mail", "reasons": str(e)}), 424


# noinspection PyUnreachableCode
@auth_bp.route("/reset", methods=["POST"])
def reset_password():
    return jsonify(error="not implemented")

    token = request.args.get("reset-key")
    decoded = decode_token(token, token_type="reset_pw")
    data = request.form.to_dict()
    if "password" not in data:
        return abort(400, "new password is required")
    user = db.session.execute(
        db.select(User).where(User.id == decoded["sub"] and User.email == decoded["aud"])).scalar_one_or_none()
    if user is None:
        return abort(404, "user not found")
    user.password = generate_password_hash(data.get("password"), method="pbkdf2", salt_length=10)
    db.session.commit()
    return jsonify({"success": "successfully changed the password"}), 200
