import json

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from db import setup_db, create_user
from middlewares import setup_middlewares
from models import User
from redis import setup_redis
from routes import setup_routes
from tests.test_view import AioHTTPTestCaseWithTestDB
from utils import generate_password_hash


class UserTestCase(AioHTTPTestCaseWithTestDB):

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
        return resp_data, user

    @unittest_run_loop
    async def test_user_list_view_OK(self):
        credentials, _ = await self._user_authorize_jwt(
            {
                'email': 'test_user_jwt_email@example.com',
                'password': 'random password',
            },
            is_superuser=True
        )
        response = await self.client.get(
            '/auth/v1/users',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
        )
        assert response.status == 200
        response_json = json.loads(await response.text())
        assert isinstance(response_json, list)

    @unittest_run_loop
    async def test_user_list_view_post_add_user(self):
        credentials, _ = await self._user_authorize_jwt(
            {
                'email': 'test_user_post_jwt_email@example.com',
                'password': 'random password 3',
            },
            is_superuser=True
        )
        response = await self.client.post(
            '/auth/v1/users',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
            data=json.dumps({
                'password': '321123',
                'is_superuser': True,
                'confirmed': True,
                'is_active': True,
                'email': 'a_newly_add_super_user2@example.com'
            })
        )
        response_json = json.loads(await response.text())
        assert response.status == 201
        assert isinstance(response_json, dict)
        assert 'password' not in response_json
        assert 'id' in response_json
        assert 'email' in response_json

        response = await self.client.post(
            '/auth/v1/users',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
            data=json.dumps({
                'is_superuser': True,
                'confirmed': True,
                'is_active': True,
                'email': 'a_newly_add_super_user3@example.com'
            })
        )
        assert response.status == 400

        response = await self.client.post(
            '/auth/v1/users',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
            data=json.dumps({
                'password': '321123',
                'is_superuser': True,
                'confirmed': True,
                'is_active': True,
                'email': 'a_newly_add_super_user2@example.com'
            })
        )
        assert response.status == 400

    @unittest_run_loop
    async def test_user_detail_view_OK(self):
        credentials, user = await self._user_authorize_jwt(
            {
                'email': 'test_user_detail_jwt_email@example.com',
                'password': 'random password 2',
            },
            is_superuser=True
        )
        response = await self.client.get(
            f'/auth/v1/users/{user.id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
        )
        assert response.status == 200
        response_json = json.loads(await response.text())
        assert isinstance(response_json, dict)

    @unittest_run_loop
    async def test_user_detail_put_view_OK(self):
        credentials, user = await self._user_authorize_jwt(
            {
                'email': 'test_user_detail_put_jwt_email@example.com',
                'password': 'random password 5',
            },
            is_superuser=True
        )
        response = await self.client.put(
            f'/auth/v1/users/{user.id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
        )
        assert response.status == 200
        response_json = json.loads(await response.text())
        assert isinstance(response_json, dict)

    @unittest_run_loop
    async def test_user_detail_patch_view_OK(self):
        credentials, user = await self._user_authorize_jwt(
            {
                'email': 'test_user_detail_patch_jwt@example.com',
                'password': 'random password 6',
            },
            is_superuser=True
        )
        response = await self.client.patch(
            f'/auth/v1/users/{user.id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
        )
        assert response.status == 200
        response_json = json.loads(await response.text())
        assert isinstance(response_json, dict)

    @unittest_run_loop
    async def test_user_delete_patch_view_OK(self):
        credentials, user = await self._user_authorize_jwt(
            {
                'email': 'test_user_delete_jwt@example.com',
                'password': 'random password 7',
            },
            is_superuser=True
        )
        response = await self.client.delete(
            f'/auth/v1/users/{user.id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {credentials["access_token"]}'
            },
        )
        assert response.status == 200
        response_json = json.loads(await response.text())
        assert isinstance(response_json, dict)
