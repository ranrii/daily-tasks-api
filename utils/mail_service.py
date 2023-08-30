import smtplib
from email.header import Header
from email.mime.text import MIMEText

from flask import current_app, jsonify

from instance.secrets import email, email_pw


def send_mail(user_data, url_key):
    if current_app.testing:
        message = "go to the link below to change the password\n"+url_key
        msg = MIMEText(message, _charset="UTF-8")
        msg["Subject"] = Header("DailyTask password reset", "utf-8")
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=email, password=email_pw)
            connection.sendmail(from_addr=email, to_addrs=user_data.email, msg=msg.as_string())
    else:
        return jsonify(error="not implemented"), 404
