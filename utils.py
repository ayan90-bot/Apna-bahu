# utils.py
import secrets
import string


def gen_key():
    # human friendly key
    return secrets.token_urlsafe(10)

# decorator helper (for handlers) - not strictly necessary but useful