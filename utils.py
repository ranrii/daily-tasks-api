import re
from datetime import datetime
from flask import abort
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
        dt_out = datetime.fromisoformat(datetime_string).replace(microsecond=0)
    except ValueError:
        return abort(400, "invalid time format provided")

    if dt_out.tzinfo is None:
        return dt_out.replace(tzinfo=pytz.utc)
    else:
        dt_out = dt_out.astimezone(tz=pytz.utc)
    return dt_out
