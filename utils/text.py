from datetime import datetime
import re
import pytz
from flask import abort


def dt_from_string(datetime_string):
    if datetime_string is None:
        return None
    try:
        dt_out = datetime.fromisoformat(datetime_string.replace("Z", "+00:00")).replace(microsecond=0)
    except ValueError:
        return abort(400, "invalid time format provided")

    dt_out = dt_out.astimezone(tz=pytz.utc)
    return dt_out


def limit_whitespace(text):
    if text is None:
        return None
    cleaned_text = re.sub(r'\s+', " ", text.strip())
    if cleaned_text in [" ", ""]:
        return None
    return cleaned_text
