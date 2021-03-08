from aiohttp import web
from schemas import register_user_schema, user_schema, message_schema
from db import create_user
from models import User
from exceptions import PasswordsDontMatch
from utils import generate_password_hash
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema
)


class UserRegister(web.View):
    @request_schema(register_user_schema)
    @response_schema(user_schema)
    @docs(
        tags=['register'],
        summary="A new user register method",
        description="This method is used for registering new user accounts",
        responses={
            200: {
                "description": "a new user successfully registered",
                "schema": user_schema
            },
            400: {
                "description": "a new user register failed",
                "schema": message_schema
            }
        }
    )
    async def post(self):
        if self.request.content_type == 'application/json':
            data = await self.request.json()
        else:
            data = await self.request.post()
        validated_data = register_user_schema.load(data)

        if validated_data.get('password') != validated_data.get('password2'):
            raise PasswordsDontMatch('Fields password and password2 don\'t match')

        user_data = {
            'email': validated_data['email'],
            'password': generate_password_hash(validated_data['password']),
            }

        async with self.request.app['db'].acquire() as conn:
            user = await create_user(conn, User, user_data)

        response = user_schema.dump(user)
        return web.json_response(response, status=200)
