from logging import Logger

from aiohttp.web_urldispatcher import UrlDispatcher

from app import init_app
from main import main
from unittest import mock


def test_app_main_run():
    run_app = mock.Mock()
    with mock.patch('aiohttp.web.run_app', run_app):
        main(argv=None)
    run_app.assert_called_once()


def test_init_app():
    app = init_app(argv=None)
    assert isinstance(app.router, UrlDispatcher)
    assert isinstance(app.logger, Logger)
    assert len(app.middlewares) >= 2
    assert len(app.router) >= 2
    assert len(app.on_startup) >= 4
