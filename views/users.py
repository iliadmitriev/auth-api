from aiohttp import web
from aiohttp_jwt import check_permissions, login_required, match_any
from pydantic import ValidationError as PydanticValidationError

from backends.db import get_objects, insert_object
from helpers.utils import generate_password_hash, get_data_from_request
from models.users import User
from schemas.users import schemas
from views.helpers.params import default_parameters

# Try to import aiohttp_apispec for documentation, but make it optional
try:
    from aiohttp_apispec import docs
    apispec_available = True
except ImportError:
    # Create a mock decorator that does nothing
    def docs(**kwargs):
        def decorator(func):
            return func
        return decorator
    apispec_available = False

# Mock responses if apispec is not available
if not apispec_available:
    responses_default = {}
    response_400 = {}
    response_404 = {}
else:
    from views.helpers.responses import response_400, response_404, responses_default


class UserListView(web.View):
    @docs(
        tags=['admin'],
        summary="Get list of users method",
        description="This method is used to get all users from db",
        parameters=default_parameters,
        responses=responses_default
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        async with self.request.app['db_session']() as session:
            profiles = await get_objects(session, User)
            result = []
            for profile in profiles:
                user_dict = {
                    'id': profile.id,
                    'email': profile.email,
                    'is_active': profile.is_active,
                    'is_superuser': profile.is_superuser,
                    'created': profile.created.isoformat() if profile.created else None,
                    'last_login': profile.last_login.isoformat() if profile.last_login else None,
                    'confirmed': profile.confirmed
                }
                result.append(user_dict)
            return web.json_response(result)

    @docs(
        tags=['admin'],
        summary="Create a new user method",
        description="This method is used to create a new user",
        parameters=default_parameters,
        responses={**responses_default, **response_400} if apispec_available else {}
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def post(self):
        async with self.request.app['db_session']() as session:
            data = await get_data_from_request(self.request)
            try:
                validated_data = schemas.user_create(**data)
            except PydanticValidationError as e:
                # Convert Pydantic validation errors to a string for error handling
                error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
                error_str = "; ".join(error_messages)
                raise ValueError(error_str)

            validated_dict = validated_data.model_dump()
            validated_dict['password'] = await generate_password_hash(validated_dict['password'])
            user = await insert_object(session, User, validated_dict)
            result = {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'created': user.created.isoformat() if user.created else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'confirmed': user.confirmed
            }
            return web.json_response(result, status=201)


class UserDetailView(web.View):
    @docs(
        tags=['admin'],
        summary="Get user by id method",
        description="This method is used to get user details by id",
        parameters=default_parameters,
        responses=responses_default if apispec_available else {}
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def get(self):
        return web.json_response({}, status=200)

    @docs(
        tags=['admin'],
        summary="Update all user details by id method",
        description="This method is used to update all user details by id",
        parameters=default_parameters,
        responses={**responses_default, **response_400, **response_404} if apispec_available else {}
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def put(self):
        return web.json_response({}, status=200)

    @docs(
        tags=['admin'],
        summary="Update user details partially by id method",
        description="This method is used to update particular user details by id",
        parameters=default_parameters,
        responses={**responses_default, **response_400, **response_404} if apispec_available else {}
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def patch(self):
        return web.json_response({}, status=200)

    @docs(
        tags=['admin'],
        summary="Delete user by id method",
        description="This method is used to delete user by id",
        parameters=default_parameters,
        responses=responses_default if apispec_available else {}
    ) if apispec_available else lambda f: f
    @login_required
    @check_permissions('admin', 'scope', comparison=match_any)
    async def delete(self):
        return web.json_response({}, status=200)
