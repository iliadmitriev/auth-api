from aiohttp.web_middlewares import middleware
from aiohttp import web
from exceptions import (
    BadRequest,
    RecordNotFound,
    PasswordsDontMatch,
    UserAlreadyExists,
    UserIsNotActivated,
    RefreshTokenNotFound
)
from json import JSONDecodeError
from marshmallow import ValidationError
from aiohttp_jwt import JWTMiddleware
from settings import SECRET_KEY


async def handle_http_error(request, e, status):
    return web.json_response(
        {
            'message': f'{type(e).__name__}: {str(e)}'
        },
        status=status
    )


jwt_middleware = JWTMiddleware(
    secret_or_pub_key=SECRET_KEY,
    request_property='user',
    algorithms=['HS256'],
    credentials_required=False
)


@middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as e:
        return await handle_http_error(request, e, status=e.status)
    except (
            BadRequest,
            JSONDecodeError,
            ValidationError,
            PasswordsDontMatch,
            UserAlreadyExists
    ) as e:
        return await handle_http_error(request, e, status=400)
    except UserIsNotActivated as e:
        return await handle_http_error(request, e, status=403)
    except (RefreshTokenNotFound, RecordNotFound) as e:
        return await handle_http_error(request, e, status=404)
    except Exception as e:
        return await handle_http_error(request, e, status=500)


def setup_middlewares(app):
    app.middlewares.append(error_middleware)
    app.middlewares.append(jwt_middleware)
