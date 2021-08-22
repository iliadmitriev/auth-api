from aiohttp import web
from aiohttp_apispec import response_schema, docs, request_schema
from aiohttp_jwt import login_required, check_permissions, match_any

from backends.db import get_objects, insert_object
from helpers.utils import get_data_from_request, generate_password_hash
from models.users import User
from schemas.users import user_schema, user_schema_partial, users_schema, message_schema
from views.helpers.params import default_parameters
from views.helpers.responses import responses_default, response_400, response_404


class UserListView(web.View):
    @response_schema(users_schema, 200, description="successfully got users list")
    @docs(
        tags=['admin'],
        summary="Get list of users method",
        description="This method is used to get all users from db",
        parameters=default_parameters,
        responses=responses_default
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        async with self.request.app['db'].acquire() as conn:
            profiles = await get_objects(conn, User)
            result = users_schema.dump(profiles, many=True)
            return web.json_response(result)

    @request_schema(user_schema)
    @response_schema(user_schema, 201, description="successfully created user")
    @docs(
        tags=['admin'],
        summary="Create a new user method",
        description="This method is used to create a new user",
        parameters=default_parameters,
        responses={**responses_default, **response_400}
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
    @response_schema(user_schema, 200, description="successfully got user details")
    @docs(
        tags=['admin'],
        summary="Get user by id method",
        description="This method is used to get user details by id",
        parameters=default_parameters,
        responses={**responses_default, **response_400}
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        return web.json_response({}, status=200)

    @request_schema(user_schema)
    @response_schema(user_schema, 200, description="successfully updated user details", )
    @docs(
        tags=['admin'],
        summary="Update all user details by id method",
        description="This method is used to update all user details by id",
        parameters=default_parameters,
        responses={**responses_default, **response_400, **response_404}
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def put(self):
        return web.json_response({}, status=200)

    @request_schema(user_schema_partial)
    @response_schema(user_schema, 200, description="successfully updated user details")
    @docs(
        tags=['admin'],
        summary="Update user details partially by id method",
        description="This method is used to update particular user details by id",
        parameters=default_parameters,
        responses={**responses_default, **response_400, **response_404}
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def patch(self):
        return web.json_response({}, status=200)

    @response_schema(user_schema, 200, description="successfully deleted user")
    @docs(
        tags=['admin'],
        summary="Delete user by id method",
        description="This method is used to delete user by id",
        parameters=default_parameters,
        responses={**responses_default, **response_404}
    )
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def delete(self):
        return web.json_response({}, status=200)
