from aiohttp import web
from aiohttp_apispec import request_schema, response_schema, docs

from app.settings import JWT_EXP_REFRESH_SECONDS
from backends.db import create_user, get_user_by_email
from backends.redis import set_redis_key, get_redis_key
from helpers.errors import PasswordsDontMatch, RecordNotFound, UserIsNotActivated, RefreshTokenNotFound
from helpers.utils import get_data_from_request, generate_password_hash, gen_token_for_user, decode_token, \
    get_refresh_token
from models.users import User
from schemas.users import register_user_schema, login_user_schema, registered_user_schema, user_schema, token_schema, \
    refresh_token_schema, message_schema


class UserRegister(web.View):
    @request_schema(register_user_schema)
    @response_schema(registered_user_schema)
    @docs(
        tags=['user'],
        summary="A new user register method",
        description="This method is used for registering new user accounts",
        responses={
            200: {
                "description": "a new user successfully registered",
                "schema": registered_user_schema
            },
            400: {
                "description": "a new user register failed",
                "schema": message_schema
            }
        }
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        validated_data = register_user_schema.load(data)

        if validated_data.get('password') != validated_data.get('password2'):
            raise PasswordsDontMatch('Fields password and password2 don\'t match')

        user_data = {
            'email': validated_data['email'],
            'password': await generate_password_hash(validated_data['password']),
            'is_active': True
        }

        async with self.request.app['db'].acquire() as conn:
            user = await create_user(conn, User, user_data)

        response = registered_user_schema.dump(user)
        return web.json_response(response, status=200)


class UserLogin(web.View):
    @request_schema(login_user_schema)
    @response_schema(token_schema)
    @docs(
        tags=['user'],
        summary="User login method",
        description="This method is used for user to log in",
        responses={
            200: {
                "description": "successfully registered",
                "schema": token_schema
            },
            400: {
                "description": "validation failed",
                "schema": message_schema
            },
            403: {
                "description": "user is not activated",
                "schema": message_schema
            },
            404: {
                "description": "user is not found or wrong email/password",
                "schema": message_schema
            },

        }
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        validated_data = login_user_schema.load(data)

        async with self.request.app['db'].acquire() as conn:
            user = await get_user_by_email(conn, User, validated_data['email'])

        password_hash = await generate_password_hash(validated_data['password'])

        if user.password != password_hash:
            raise RecordNotFound(f'{User.__name__} with email={validated_data["email"]} is not found')

        user_data = user_schema.dump(user)

        if not user_data.get('is_active'):
            raise UserIsNotActivated(f'{User.__name__} with email={validated_data["email"]} is not activated')

        token = await gen_token_for_user(user_data)

        await set_redis_key(self.request.app['redis'], token['refresh_token'], '1', JWT_EXP_REFRESH_SECONDS)

        response = token_schema.dump(token)
        return web.json_response(response, status=200)


class RefreshToken(web.View):
    @request_schema(refresh_token_schema)
    @response_schema(token_schema)
    @docs(
        tags=['user'],
        summary="Refresh token method",
        description="This method is used to refresh access token for user",
        responses={
            200: {
                "description": "successfully refreshed token",
                "schema": token_schema
            },
            400: {
                "description": "validation failed",
                "schema": message_schema
            },
            403: {
                "description": "user is not activated",
                "schema": message_schema
            },
            404: {
                "description": "user is not found or wrong email/password",
                "schema": message_schema
            },
        }
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        validated_data = refresh_token_schema.load(data)
        cache = await get_redis_key(self.request.app['redis'], validated_data['refresh_token'])
        if not cache:
            raise RefreshTokenNotFound('Refresh token not found')
        payload = await decode_token(validated_data['refresh_token'])
        token = await get_refresh_token(payload)
        response = token_schema.dump(token)
        return web.json_response(response, status=200)