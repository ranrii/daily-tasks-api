import re
from datetime import datetime
from flask import abort, request
import pytz
from urllib.parse import unquote


def limit_whitespace(text):
    if text is None:
        return None
    cleaned_text = re.sub(r'\s+', " ", text.strip())
    if cleaned_text in [" ", ""]:
        return None
    return cleaned_text


def dt_from_string(datetime_string):
    if datetime_string is None:
        return None
    try:
        dt_out = datetime.fromisoformat(datetime_string.replace("Z", "+00:00")).replace(microsecond=0)
    except ValueError:
        return abort(400, "invalid time format provided")

    dt_out = dt_out.astimezone(tz=pytz.utc)
    return dt_out


def get_ip_addr():
    return request.headers.get("x-Forwarded-For", request.headers.get("X-Real-IP", request.remote_addr))