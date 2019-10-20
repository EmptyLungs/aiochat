import asyncio
import logging

import aioredis
import peewee_async
import aiohttp_cors
from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher
from aiohttp_session import session_middleware
from aiohttp_session.redis_storage import RedisStorage

from db import database
from utils.middlewares import request_user_middleware
from settings import REDIS_CON, DATABASE
from views import Test, WebSocket, LogInView, UserInfoView, RoomListView

router = UrlDispatcher()

loop = asyncio.get_event_loop()
redis_pool = loop.run_until_complete(aioredis.create_pool(REDIS_CON, loop=loop))
middlewares = [session_middleware(RedisStorage(redis_pool=redis_pool, cookie_name='aiochat_session_id', 
                                               max_age=24*60*60, domain="192.168.0.101", httponly=False, secure=False)), 
               request_user_middleware]
app = web.Application(router=router, middlewares=middlewares)

cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
      allow_credentials=True,
      expose_headers="*",
      allow_headers="*"
  )
})
cors.add(router.add_post('/login', LogInView))
cors.add(router.add_get('/ws/{slug}', WebSocket))
cors.add(router.add_get('/user_info', UserInfoView))
cors.add(router.add_get('/room_list', RoomListView))

app.redis_pool = redis_pool
app.ws_connections = {}

database.init(**DATABASE)
app.database = database
app.database.set_allow_sync(False)
app.objects = peewee_async.Manager(app.database)

logging.basicConfig(level=logging.DEBUG)

web.run_app(app, host='0.0.0.0', port=8001)
