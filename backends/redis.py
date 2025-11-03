import redis.asyncio as redis


async def init_redis(app):
    # Explicitly await the from_url coroutine
    redis_client = await redis.from_url(app['redis_location'])
    app['redis'] = redis_client


async def close_redis(app):
    await app['redis'].close()


def setup_redis(app, redis_location):
    app['redis_location'] = redis_location
    app.on_startup.append(init_redis)
    app.on_cleanup.append(close_redis)


async def get_redis_key(redis_client, key):
    val = await redis_client.get(key)
    return val


async def set_redis_key(redis_client, key, value, expire=None):
    if expire is None:
        res = await redis_client.set(key, value)
    else:
        res = await redis_client.set(key, value, ex=expire)
    return res
