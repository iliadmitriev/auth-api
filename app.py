from aiohttp import web
from routes import setup_routes
from aiohttp_apispec import setup_aiohttp_apispec
import sys
import logging

from db import setup_db
from redis import setup_redis
from middlewares import setup_middlewares
from settings import dsn, access_log_format, APP_PORT, APP_HOST, redis_location


async def init_app(argv=None):
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


def main(argv):
    logging.basicConfig(level=logging.INFO)
    app = init_app(argv)
    web.run_app(
        app,
        access_log_format=access_log_format,
        host=APP_HOST,
        port=APP_PORT
    )


if __name__ == '__main__':
    main(sys.argv[1:])
