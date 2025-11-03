from aiohttp import web
from pydantic import ValidationError as PydanticValidationError

from app.settings import JWT_EXP_REFRESH_SECONDS
from backends.db import create_user, get_user_by_email
from backends.redis import get_redis_key, set_redis_key
from helpers.errors import (
    PasswordsDontMatch,
    RecordNotFound,
    RefreshTokenNotFound,
    UserIsNotActivated,
)
from helpers.utils import (
    decode_token,
    gen_token_for_user,
    generate_password_hash,
    get_data_from_request,
    get_refresh_token,
)
from models.users import User
from schemas.users import schemas

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


class UserRegister(web.View):
    @(
        docs(
            tags=["user"],
            summary="A new user register method",
            description="This method is used for registering new user accounts",
            responses={
                200: {
                    "description": "a new user successfully registered",
                },
                400: {
                    "description": "a new user register failed",
                },
            },
        )
        if apispec_available
        else lambda f: f
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        try:
            validated_data = schemas.registration(**data)
        except PydanticValidationError as e:
            # Convert Pydantic validation errors to a string for error handling
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            error_str = "; ".join(error_messages)
            raise ValueError(error_str) from e

        if validated_data.password != validated_data.password2:
            raise PasswordsDontMatch("Fields password and password2 don't match")

        user_data = {
            "email": validated_data.email,
            "password": await generate_password_hash(validated_data.password),
            "is_active": True,
        }

        async with self.request.app["db_session"]() as session:
            user = await create_user(session, User, user_data)

        # Convert SQLAlchemy object to dict for JSON response
        response_data = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "created": user.created.isoformat() if user.created else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        return web.json_response(response_data, status=200)


class UserLogin(web.View):
    @(
        docs(
            tags=["user"],
            summary="User login method",
            description="This method is used for user to log in",
            responses={
                200: {
                    "description": "successfully registered",
                },
                400: {
                    "description": "validation failed",
                },
                403: {
                    "description": "user is not activated",
                },
                404: {
                    "description": "user is not found or wrong email/password",
                },
            },
        )
        if apispec_available
        else lambda f: f
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        try:
            validated_data = schemas.login(**data)
        except PydanticValidationError as e:
            # Convert Pydantic validation errors to a string for error handling
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            error_str = "; ".join(error_messages)
            raise ValueError(error_str) from e

        async with self.request.app["db_session"]() as session:
            user = await get_user_by_email(session, User, validated_data.email)

        password_hash = await generate_password_hash(validated_data.password)

        if user.password != password_hash:
            raise RecordNotFound(
                f"{User.__name__} with email={validated_data.email} is not found"
            )

        user_dict = {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
        }

        if not user.is_active:
            raise UserIsNotActivated(
                f"{User.__name__} with email={validated_data.email} is not activated"
            )

        token = await gen_token_for_user(user_dict)

        await set_redis_key(
            self.request.app["redis"],
            token["refresh_token"],
            "1",
            JWT_EXP_REFRESH_SECONDS,
        )

        return web.json_response(token, status=200)


class RefreshToken(web.View):
    @(
        docs(
            tags=["user"],
            summary="Refresh token method",
            description="This method is used to refresh access token for user",
            responses={
                200: {
                    "description": "successfully refreshed token",
                },
                400: {
                    "description": "validation failed",
                },
                403: {
                    "description": "user is not activated",
                },
                404: {
                    "description": "user is not found or wrong email/password",
                },
            },
        )
        if apispec_available
        else lambda f: f
    )
    async def post(self):
        data = await get_data_from_request(self.request)
        try:
            validated_data = schemas.refresh_token(**data)
        except PydanticValidationError as e:
            # Convert Pydantic validation errors to a string for error handling
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            error_str = "; ".join(error_messages)
            raise ValueError(error_str) from e

        cache = await get_redis_key(
            self.request.app["redis"], validated_data.refresh_token
        )
        if not cache:
            raise RefreshTokenNotFound("Refresh token not found")
        payload = await decode_token(validated_data.refresh_token)
        token = await get_refresh_token(payload)
        return web.json_response(token, status=200)
