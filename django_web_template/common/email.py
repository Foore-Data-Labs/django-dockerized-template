import re


def is_valid_email(email):
    return email and re.match(r"[^@]+@[^@]+\.[^@]+", email)
