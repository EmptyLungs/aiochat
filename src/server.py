import asyncio

from aiohttp import web
from aiohttp.web_urldispatcher import UrlDispatcher

router = UrlDispatcher()

app = web.Application(router=router)

#loop = asyncio.get_event_loop()

web.run_app(app, host='0.0.0.0', port=8001)