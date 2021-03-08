import hashlib
from base64 import b64encode
from settings import SECRET_KEY


def generate_password_hash(passwd: str) -> str:
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        passwd.encode('utf-8'),
        SECRET_KEY.encode('utf-8'),
        1000
    )
    return b64encode(dk).decode('ascii').strip()

