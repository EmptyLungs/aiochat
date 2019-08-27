from aiohttp import web


class Test(web.View):
    async def get(self):
        return web.json_response({"data": {"message": "Hello World!"}})
