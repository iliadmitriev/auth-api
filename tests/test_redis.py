import asyncio
import sys
from asyncio import Future
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest

from backends.redis import (
    close_redis,
    get_redis_key,
    init_redis,
    set_redis_key,
    setup_redis,
)


async def test_init_redis():
    app = {"redis_location": "redis.example.com"}
    # Create an async mock that returns a mock redis client when awaited
    mock_redis_client = AsyncMock()
    from_url_mock = AsyncMock(return_value=mock_redis_client)
    with mock.patch("redis.asyncio.from_url", from_url_mock):
        await init_redis(app)

    from_url_mock.assert_called_once_with(app["redis_location"])
    assert app["redis"] == mock_redis_client


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


async def test_redis_close():
    close_mock = MagicMock(return_value=async_return(None))
    app = {"redis": lambda: None}
    app["redis"].close = close_mock
    await close_redis(app)
    close_mock.assert_called_once()


def test_setup_redis():
    class App:
        def __init__(self):
            self.on_startup = mock.Mock()
            self.on_cleanup = mock.Mock()

        def __getitem__(self, item):
            return getattr(self, item)

        def __setitem__(self, item, value):
            return setattr(self, item, value)

    app = App()
    setup_redis(app=app, redis_location="redis location")
    assert app["redis_location"] == "redis location"
    app.on_startup.append.assert_called_once_with(init_redis)
    app.on_cleanup.append.assert_called_once_with(close_redis)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_set_redis_key():
    redis = mock.AsyncMock()
    redis.set.return_value = True
    res = await set_redis_key(redis_client=redis, key="test key", value="test value")
    redis.set.assert_called_once_with("test key", "test value")
    assert res


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_set_redis_key_with_expire():
    redis = mock.AsyncMock()
    redis.set.return_value = True
    res = await set_redis_key(
        redis_client=redis, key="test key", value="test value", expire=1000
    )
    redis.set.assert_called_once_with("test key", "test value", ex=1000)
    assert res


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
async def test_get_redis_key():
    redis = mock.AsyncMock()
    redis.get.return_value = True
    res = await get_redis_key(redis_client=redis, key="test key")
    redis.get.assert_called_once_with("test key")
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
