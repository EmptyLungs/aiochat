import asyncio

import aioredis
import peewee_async
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

from db import database
from utils.middlewares import request_user_middleware
from settings import REDIS_CON, DATABASE

from views import Test

async def start_app(pool):
    router = UrlDispatcher()
    router.add_get('/', Test)
    loop = asyncio.get_event_loop()
    redis_pool = await aioredis.create_pool(REDIS_CON, loop=loop)
    middlewares = [session_middleware(RedisStorage(redis_pool=redis_pool, cookie_name='aiochat_session_id')), request_user_middleware]
    app = web.Application(router=router, middlewares=middlewares)
    app.redis_pool = redis_pool

    database.init(**DATABASE)
    app.database = database
    app.database.set_allow_sync(False)
    app.objects = peewee_async.Manager(app.database)
    # web.run_app(app, host='0.0.0.0', port=8001)
    server_handler = app.make_handler()
    server_gen = loop.create_server(server_handler, '0.0.0.0', 8001)
    return server_gen, server_handler, app

async def stop_app(server, app, handler):
    server.close()
    await server.wait_closed()
    app.redis_pool.close()
    await app.redis_pool.wait_closed()
    await app.objects.close()
    await app.shutdown()
    await app.cleanup()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server_gen, handler, app = loop.run_until_complete(start_app(loop))
    server = loop.run_until_complete(server_gen)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Keyboard interrupt')
    finally:
        loop.run_until_complete(stop_app(server, app, handler))
        loop.close()
    print('Server killed')
