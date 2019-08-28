import asyncio
import logging

import aioredis
import peewee_async
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

from db import database
from utils.middlewares import request_user_middleware
from settings import REDIS_CON, DATABASE

from views import Test, WebSocket, LogInView

router = UrlDispatcher()
router.add_get('/', Test)
router.add_get('/ws', WebSocket)
router.add_post('/login', LogInView)

loop = asyncio.get_event_loop()
redis_pool = loop.run_until_complete(aioredis.create_pool(REDIS_CON, loop=loop))
middlewares = [session_middleware(RedisStorage(redis_pool=redis_pool, cookie_name='aiochat_session_id', max_age=500)), 
               request_user_middleware]
app = web.Application(router=router, middlewares=middlewares)
app.redis_pool = redis_pool
app.ws_connections = {}

database.init(**DATABASE)
app.database = database
app.database.set_allow_sync(False)
app.objects = peewee_async.Manager(app.database)

logging.basicConfig(level=logging.DEBUG)

web.run_app(app, host='0.0.0.0', port=8001)
