from logging import Logger
from unittest import mock

from aiohttp.web_urldispatcher import UrlDispatcher

from app import init_app
from main import main


def test_app_main_run():
    run_app = mock.Mock()
    with mock.patch("aiohttp.web.run_app", run_app):
        main(argv=None)
    run_app.assert_called_once()


def test_init_app():
    app = init_app(argv=None)
    assert isinstance(app.router, UrlDispatcher)
    assert isinstance(app.logger, Logger)
    assert len(app.middlewares) >= 2
    assert len(app.router) >= 2
    # We now have 3 startup handlers (pg init, redis init, and cleanup context)
    # instead of 4 because apispec is optional
    assert len(app.on_startup) >= 3
