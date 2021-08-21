import hashlib
from datetime import datetime, timedelta
import jwt
from base64 import b64encode
from app.settings import (
    SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXP_ACCESS_SECONDS,
    JWT_EXP_REFRESH_SECONDS
)
from uuid import uuid4


async def generate_password_hash(passwd: str) -> str:
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        passwd.encode('utf-8'),
        SECRET_KEY.encode('utf-8'),
        1000
    )
    return b64encode(dk).decode('ascii').strip()


async def get_data_from_request(request):
    if request.content_type == 'application/json':
        data = await request.json()
    else:
        data = await request.post()
    return data


async def gen_token_for_user(user):
    token = {
        'user_id': user.get('id'),
        'email': user.get('email'),
        'jti': uuid4().hex,
    }

    if user.get('is_superuser'):
        token['scope'] = 'admin'

    access_token = {
        **token,
        'token_type': 'access_token',
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_ACCESS_SECONDS)
    }

    refresh_token = {
        **token,
        'token_type': 'refresh_token',
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_REFRESH_SECONDS)
    }

    return {
        "access_token": jwt.encode(access_token, SECRET_KEY, JWT_ALGORITHM),
        "refresh_token": jwt.encode(refresh_token, SECRET_KEY, JWT_ALGORITHM)
    }


async def decode_token(token):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[JWT_ALGORITHM]
    )
    return payload


async def get_refresh_token(token):
    token['jti'] = uuid4().hex
    access_token = {
        **token,
        'token_type': 'access_token',
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXP_ACCESS_SECONDS)
    }

    refresh_token = {
        **token,
        'token_type': 'refresh_token',
    }

    return {
        "access_token": jwt.encode(access_token, SECRET_KEY, JWT_ALGORITHM),
        "refresh_token": jwt.encode(refresh_token, SECRET_KEY, JWT_ALGORITHM)
    }
