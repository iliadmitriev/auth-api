import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from db import setup_db
from middlewares import setup_middlewares
from routes import setup_routes


@pytest.mark.usefixtures('get_dsn')
class AioHTTPTestCaseWithTestDB(AioHTTPTestCase):

    async def get_application(self):
        app = web.Application()
        setup_routes(app)
        setup_middlewares(app)
        setup_db(app, self.dsn)
        self.app = app
        return app


class UserRegistrationTestCase(AioHTTPTestCaseWithTestDB):
    @unittest_run_loop
    async def test_auth_register_get_405(self):
        resp = await self.client.get('/auth/v1/register')
        assert resp.status == 405
