import asyncio
import sys
from asyncio import Future
from unittest import mock
from unittest.mock import MagicMock

import pytest

from redis import init_redis, close_redis, setup_redis, set_redis_key, get_redis_key


async def test_init_redis():
    app = {
        'redis_location': 'redis.example.com'
    }
    from_url_mock = mock.Mock(return_value='test redis server')
    with mock.patch('aioredis.from_url', from_url_mock):
        await init_redis(app)

    from_url_mock.assert_called_once_with(app['redis_location'])
    assert app['redis'] == 'test redis server'


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


async def test_redis_close():
    close_mock = MagicMock(return_value=async_return(None))
    app = {'redis': lambda: None}
    app['redis'].close = close_mock
    await close_redis(app)
    close_mock.assert_called_once()


def test_setup_redis():
    class App(object):
        def __init__(self):
            self.on_startup = mock.Mock()
            self.on_cleanup = mock.Mock()

        def __getitem__(self, item):
            return getattr(self, item)

        def __setitem__(self, item, value):
            return setattr(self, item, value)

    app = App()
    setup_redis(app=app, redis_location='redis location')
    assert app['redis_location'] == 'redis location'
    app.on_startup.append.assert_called_once_with(init_redis)
    app.on_cleanup.append.assert_called_once_with(close_redis)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_set_redis_key():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(redis=redis, key='test key', value='test value')
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with('test key', 'test value')
    assert res


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_set_redis_key_with_expire():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.set.return_value = True
    res = await set_redis_key(redis=redis, key='test key', value='test value', expire=1000)
    redis.client.return_value.__aenter__.return_value.set.assert_called_once_with('test key', 'test value', ex=1000)
    assert res


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_get_redis_key():
    redis = mock.MagicMock()
    redis.client.return_value.__aenter__.return_value.get.return_value = True
    res = await get_redis_key(redis=redis, key='test key')
    redis.client.return_value.__aenter__.return_value.get.assert_called_once_with('test key')
    assert res


class AMagicMock(MagicMock):
    async def __aenter__(self):
        val = mock.MagicMock()
        f = Future()
        f.set_result(True)
        val.set = MagicMock(return_value=f)
        val.get = MagicMock(return_value=f)
        return val

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.skipif(sys.version_info > (3, 8) or sys.version_info <= (3, 7), reason="requires python3.7")
async def test_set_redis_key_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await set_redis_key(redis=redis, key='test key', value='test value')
    assert res


@pytest.mark.skipif(sys.version_info > (3, 8) or sys.version_info <= (3, 7), reason="requires python3.7")
async def test_set_redis_key_with_expire_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await set_redis_key(redis=redis, key='test key', value='test value', expire=1000)
    assert res


@pytest.mark.skipif(sys.version_info > (3, 8) or sys.version_info <= (3, 7), reason="requires python3.7")
async def test_set_redis_key_with_expire_py_3_7():
    redis = mock.MagicMock()
    redis.client.return_value = AMagicMock()
    res = await get_redis_key(redis=redis, key='test key')
    assert res
