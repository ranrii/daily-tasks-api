import re


def limit_whitespace(text):
    if text is None:
        return None
    cleaned_text = re.sub(r'\s+', " ", text.strip())
    if cleaned_text == " ":
        return None
    return cleaned_text
