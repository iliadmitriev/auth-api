from unittest.mock import AsyncMock, MagicMock

import pytest

from backends.redis import (
    close_redis,
    get_redis_key,
    init_redis,
    set_redis_key,
    setup_redis,
)


class TestRedisBackend:
    """Test Redis backend functions"""

    async def test_init_redis(self):
        # Mock app and redis
        app = {}
        redis_location = "redis://localhost:6379"
        app["redis_location"] = redis_location

        # Mock redis.from_url to return a mock redis client
        mock_redis_client = AsyncMock()
        with pytest.MonkeyPatch().context() as m:
            mock_redis_module = MagicMock()
            # Create a proper async mock that when awaited returns our client
            mock_from_url = AsyncMock(return_value=mock_redis_client)
            mock_redis_module.from_url = mock_from_url
            m.setattr("backends.redis.redis", mock_redis_module)

            await init_redis(app)
            assert "redis" in app
            # The redis client should have been created from the URL
            mock_from_url.assert_called_once_with("redis://localhost:6379")

    async def test_close_redis(self):
        # Mock app with redis client
        mock_redis_client = AsyncMock()
        app = {"redis": mock_redis_client}

        await close_redis(app)
        mock_redis_client.close.assert_called_once()

    def test_setup_redis(self):
        # Mock app with proper aiohttp app structure
        class MockApp:
            def __init__(self):
                self.on_startup = []
                self.on_cleanup = []
                self.data = {}

            def __setitem__(self, key, value):
                self.data[key] = value

            def __getitem__(self, key):
                return self.data[key]

        app = MockApp()
        redis_location = "redis://localhost:6379"

        setup_redis(app, redis_location)

        assert app["redis_location"] == redis_location
        assert len(app.on_startup) == 1
        assert len(app.on_cleanup) == 1
        assert app.on_startup[0] == init_redis
        assert app.on_cleanup[0] == close_redis

    async def test_get_redis_key(self):
        # Mock redis client
        mock_redis_client = AsyncMock()
        mock_redis_client.get = AsyncMock(return_value="test_value")

        result = await get_redis_key(mock_redis_client, "test_key")
        assert result == "test_value"
        mock_redis_client.get.assert_called_once_with("test_key")

    async def test_set_redis_key_without_expire(self):
        # Mock redis client
        mock_redis_client = AsyncMock()
        mock_redis_client.set = AsyncMock(return_value=True)

        result = await set_redis_key(mock_redis_client, "test_key", "test_value")
        assert result is True
        mock_redis_client.set.assert_called_once_with("test_key", "test_value")

    async def test_set_redis_key_with_expire(self):
        # Mock redis client
        mock_redis_client = AsyncMock()
        mock_redis_client.set = AsyncMock(return_value=True)

        result = await set_redis_key(
            mock_redis_client, "test_key", "test_value", expire=100
        )
        assert result is True
        mock_redis_client.set.assert_called_once_with("test_key", "test_value", ex=100)
