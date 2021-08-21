from aiohttp import web
from aiohttp_apispec import setup_aiohttp_apispec

from app.middlewares import setup_middlewares
from app.settings import dsn, redis_location
from backends.db import setup_db
from backends.redis import setup_redis
from routes.auth import setup_routes


def init_app(argv=None):
    app = web.Application()

    setup_routes(app)
    setup_aiohttp_apispec(
        app=app,
        title="Auth documentation",
        version="v1",
        url="/auth/v1/docs/swagger.json",
        swagger_path="/auth/v1/docs",
        static_path="/auth/static"
    )
    setup_middlewares(app)
    setup_db(app, dsn=dsn)
    setup_redis(app, redis_location=redis_location)

    return app
