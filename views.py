from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema
)
from aiohttp_jwt import login_required, check_permissions, match_any

from db import (
    create_user,
    get_user_by_email, get_objects, insert_object
)
from exceptions import (
    PasswordsDontMatch,
    RecordNotFound,
    UserIsNotActivated,
    RefreshTokenNotFound
)
from models import User
from redis import (
    get_redis_key,
    set_redis_key
)
from schemas import (
    register_user_schema,
    user_schema,
    registered_user_schema,
    message_schema,
    login_user_schema,
    token_schema,
    refresh_token_schema,
    users_schema,
    user_schema_partial
)
from settings import JWT_EXP_REFRESH_SECONDS
from utils import (
    generate_password_hash,
    get_data_from_request,
    gen_token_for_user,
    decode_token,
    get_refresh_token
)

default_parameters = [{
    'in': 'header',
    'name': 'Authorization',
    'type': 'string',
    'format': 'Bearer',
    'required': 'true'
}]


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


class UserListView(web.View):
    @response_schema(users_schema)
    @docs(
        tags=['admin'],
        summary="Get list of users method",
        description="This method is used to get all users from db",
        parameters=default_parameters,
        responses={
            200: {
                "description": "successfully got users list",
                "schema": users_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            profiles = await get_objects(conn, User)
            result = users_schema.dump(profiles, many=True)
            return web.json_response(result)

    @request_schema(user_schema)
    @response_schema(user_schema)
    @docs(
        tags=['admin'],
        summary="Create a new user method",
        description="This method is used to create a new user",
        parameters=default_parameters,
        responses={
            201: {
                "description": "successfully created user",
                "schema": user_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            data = await get_data_from_request(self.request)
            validated_data = user_schema.load(data)
            validated_data['password'] = await generate_password_hash(validated_data['password'])
            user = await insert_object(conn, User, validated_data)
            result = user_schema.dump(user)
            return web.json_response(result, status=201)


class UserDetailView(web.View):
    @response_schema(user_schema)
    @docs(
        tags=['admin'],
        summary="Get user by id method",
        description="This method is used to get all user details by id",
        responses={
            200: {
                "description": "successfully got user details",
                "schema": users_schema
            },
            404: {
                "description": "user not found",
                "schema": message_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        return web.json_response({}, status=200)

    @request_schema(user_schema)
    @response_schema(user_schema)
    @docs(
        tags=['admin'],
        summary="Update all user details by id method",
        description="This method is used to update all user details by id",
        responses={
            200: {
                "description": "successfully updated user details",
                "schema": user_schema
            },
            404: {
                "description": "user not found",
                "schema": message_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def put(self):
        return web.json_response({}, status=200)

    @request_schema(user_schema_partial)
    @response_schema(user_schema)
    @docs(
        tags=['admin'],
        summary="Update user details partially by id method",
        description="This method is used to update particular user details by id",
        responses={
            200: {
                "description": "successfully updated user details",
                "schema": user_schema
            },
            404: {
                "description": "user not found",
                "schema": message_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def patch(self):
        return web.json_response({}, status=200)

    @response_schema(user_schema)
    @docs(
        tags=['admin'],
        summary="Delete user by id method",
        description="This method is used to delete user by id",
        responses={
            200: {
                "description": "successfully deleted user",
                "schema": user_schema
            },
            404: {
                "description": "user not found",
                "schema": message_schema
            },
        }
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def delete(self):
        return web.json_response({}, status=200)
