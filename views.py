from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema
)
from models import User
from exceptions import PasswordsDontMatch, RecordNotFound, UserIsNotActivated
from utils import (
    generate_password_hash,
    get_data_from_request,
    gen_token_for_user
)
from db import (
    create_user,
    get_user_by_email
)
from redis import (
    get_redis_key,
    set_redis_key
)
from schemas import (
    register_user_schema,
    user_schema,
    message_schema,
    login_user_schema,
    token_schema
)
from settings import JWT_EXP_REFRESH_SECONDS


class UserRegister(web.View):
    @request_schema(register_user_schema)
    @response_schema(user_schema)
    @docs(
        tags=['user'],
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
        data = get_data_from_request(self.request)
        validated_data = register_user_schema.load(data)

        if validated_data.get('password') != validated_data.get('password2'):
            raise PasswordsDontMatch('Fields password and password2 don\'t match')

        user_data = {
            'email': validated_data['email'],
            'password': await generate_password_hash(validated_data['password']),
        }

        async with self.request.app['db'].acquire() as conn:
            user = await create_user(conn, User, user_data)

        response = user_schema.dump(user)
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
                "description": "user is not found or wrong email or password",
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
