import smtplib
from email.header import Header
from email.mime.text import MIMEText

from email_validator import validate_email, EmailNotValidError
from flask import current_app, jsonify, abort


def send_mail(user_data, url_key):
    if current_app.testing:
        message = "go to the link below to change the password\n"+url_key
        msg = MIMEText(message, _charset="UTF-8")
        msg["Subject"] = Header("DailyTask password reset", "utf-8")
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=current_app.config.get("EMAIL"), password=current_app.config.get("M_PW"))
            connection.sendmail(
                from_addr=current_app.config.get("EMAIL"), to_addrs=user_data.email, msg=msg.as_string())
    else:
        return jsonify(error="not implemented"), 501


def check_email(user_email):
    if user_email is None:
        return abort(400, "no email provided")
    try:
        email_info = validate_email(user_email, check_deliverability=current_app.config["REAL_MAIL"])
    except EmailNotValidError as e:
        return abort(400, str(e))
    return email_info.normalized
