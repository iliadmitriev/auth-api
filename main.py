import logging
import sys

from aiohttp import web

from app import init_app
from app.settings import APP_HOST, APP_PORT, access_log_format


def main(argv):
    logging.basicConfig(level=logging.INFO)
    app = init_app(argv)
    web.run_app(
        app,
        access_log_format=access_log_format,
        host=APP_HOST,
        port=int(APP_PORT),  # Convert to int to satisfy aiohttp
    )


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
