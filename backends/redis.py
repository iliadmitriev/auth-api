import aioredis


async def init_redis(app):
    app['redis'] = aioredis.from_url(
        app['redis_location'],
    )


async def close_redis(app):
    await app['redis'].close()


def setup_redis(app, redis_location):
    app['redis_location'] = redis_location
    app.on_startup.append(init_redis)
    app.on_cleanup.append(close_redis)


async def get_redis_key(redis, key):
    async with redis.client() as conn:
        val = await conn.get(key)
    return val


async def set_redis_key(redis, key, value, expire=None):
    async with redis.client() as conn:
        if expire is None:
            res = await conn.set(key, value)
        else:
            res = await conn.set(key, value, ex=expire)
    return res
