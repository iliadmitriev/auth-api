import aioredis


async def init_redis(app):
    pool = await aioredis.create_pool(
        app['redis_location'],
        minsize=5, maxsize=10)
    app['redis'] = pool


async def close_redis(app):
    pool = app['redis']
    pool.close()
    await pool.wait_closed()


def setup_redis(app, redis_location):
    app['redis_location'] = redis_location
    app.on_startup.append(init_redis)
    app.on_cleanup.append(close_redis)


async def get_redis_key(redis, key):
    with await redis as conn:
        val = await conn.execute('get', key)
    return val


async def set_redis_key(redis, key, value, expire=None):
    with await redis as conn:
        if expire is None:
            res = await conn.execute('set', key, value)
        else:
            res = await conn.execute('set', key, value, 'ex', expire)
    return res
