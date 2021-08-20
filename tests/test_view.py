import json

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from db import setup_db, create_user
from redis import setup_redis
from middlewares import setup_middlewares
from models import User
from routes import setup_routes
from utils import generate_password_hash, decode_token


@pytest.mark.usefixtures('get_dsn')
class AioHTTPTestCaseWithTestDB(AioHTTPTestCase):

    async def get_application(self):
        app = web.Application()
        setup_routes(app)
        setup_middlewares(app)
        setup_db(app, self.dsn)
        setup_redis(app, self.redis_location)
        self.app = app
        return app


class UserRegistrationTestCase(AioHTTPTestCaseWithTestDB):
    async def _create_user(self, data):
        user_data = {
            'email': data.get('email'),
            'password': await generate_password_hash(data.get('password')),
            'is_active': data.get('is_active', False),
            'is_superuser': data.get('is_superuser', False)
        }
        async with self.app['db'].acquire() as conn:
            user = await create_user(conn, User, user_data)
        assert user is not None
        return user

    @unittest_run_loop
    async def test_auth_register_get_405(self):
        resp = await self.client.get('/auth/v1/register')
        assert resp.status == 405

    @unittest_run_loop
    async def test_auth_register_post_invalid_email(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'invalid-email',
            'password': 'secret',
            'password2': 'secret2',
        }
        resp = await self.client.post(
            '/auth/v1/register',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 400

    @unittest_run_loop
    async def test_auth_register_post_password_dont_match(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123@example.com',
            'password': 'secret',
            'password2': 'secret2',
        }
        resp = await self.client.post(
            '/auth/v1/register',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 400

    @unittest_run_loop
    async def test_auth_register_user_exists(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user1234@example.com',
            'password': 'secret',
            'password2': 'secret',
        }
        resp = await self.client.post(
            '/auth/v1/register',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 200
        resp = await self.client.post(
            '/auth/v1/register',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 400

    @unittest_run_loop
    async def test_auth_register_post_200(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123reg@example.com',
            'password': 'secret',
            'password2': 'secret',
        }
        resp = await self.client.post(
            '/auth/v1/register',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 200

    @unittest_run_loop
    async def test_auth_login_post_200(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123login@example.com',
            'password': 'secret'
        }
        await self._create_user(data={
            **data,
            'is_active': True
        })

        resp = await self.client.post(
            '/auth/v1/login',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 200

    @unittest_run_loop
    async def test_auth_login_post_404_wrong_password(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123login_next@example.com',
            'password': 'secret_new',
        }
        await self._create_user(data={
            'email': data.get('email'),
            'password': 'secret_old',
            'is_active': True
        })

        resp = await self.client.post(
            '/auth/v1/login',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 404

    @unittest_run_loop
    async def test_auth_login_post_403_user_is_not_active(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123login_not_active@example.com',
            'password': 'secret_new',
        }
        await self._create_user(data={
            **data,
            'is_active': False
        })

        resp = await self.client.post(
            '/auth/v1/login',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 403

    @unittest_run_loop
    async def test_auth_login_post_404_non_existent_user(self):
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'email': 'user123login_not_exists@example.com',
            'password': 'secret',
        }
        resp = await self.client.post(
            '/auth/v1/login',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 404

    async def _user_authorize_jwt(self, data, is_superuser=False):
        headers = {
            'Content-Type': 'application/json'
        }
        user = await self._create_user(data={
            **data,
            'is_superuser': is_superuser,
            'is_active': True
        })
        assert user is not None
        resp = await self.client.post(
            '/auth/v1/login',
            data=json.dumps(data),
            headers=headers
        )
        assert resp.status == 200
        resp_data = json.loads(await resp.text())
        assert 'access_token' in resp_data
        assert 'refresh_token' in resp_data
        return resp_data

    @unittest_run_loop
    async def test_auth_token_200_super_user_OK(self):
        resp_data = await self._user_authorize_jwt(
            data={
                'email': 'user1_admin_with_token1@example.com',
                'password': 'secret'
            },
            is_superuser=True
        )
        token = await decode_token(resp_data.get('access_token'))
        assert token.get('scope') == 'admin'

    @unittest_run_loop
    async def test_auth_refresh_token_200_OK(self):
        resp_data = await self._user_authorize_jwt(data={
            'email': 'user1_with_token1@example.com',
            'password': 'secret',
        })

        resp_refresh = await self.client.post(
            '/auth/v1/refresh',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'refresh_token': resp_data.get('refresh_token')
            })
        )
        refresh_data = json.loads(await resp_refresh.text())
        assert resp_refresh.status == 200
        assert 'access_token' in refresh_data
        assert 'refresh_token' in refresh_data

    @unittest_run_loop
    async def test_auth_refresh_token_not_found(self):
        resp_data = await self._user_authorize_jwt(data={
            'email': 'user1_with_token2@example.com',
            'password': 'secret',
        })

        resp_refresh = await self.client.post(
            '/auth/v1/refresh',
            data={
                'refresh_token': 'random not existent token'
            }
        )
        assert resp_refresh.status == 404
