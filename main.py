import logging
import sys

from aiohttp import web

from app import init_app
from app.settings import access_log_format, APP_HOST, APP_PORT


def main(argv):
    logging.basicConfig(level=logging.INFO)
    app = init_app(argv)
    web.run_app(
        app,
        access_log_format=access_log_format,
        host=APP_HOST,
        port=APP_PORT
    )


if __name__ == '__main__':  # pragma: no cover
    main(sys.argv[1:])
