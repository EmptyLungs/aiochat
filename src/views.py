from time import time

from aiohttp import web, WSMsgType

from models import Message, User


class BaseView(web.View):
    login_required = False
    async def _iter(self):
        if self.login_required and self.request.user is None:
            return web.HTTPUnauthorized()
        return await super()._iter()


class Test(BaseView):
    async def get(self):
        return web.json_response({"data": {"message": "Hello World!"}})


class WebSocket(BaseView):
    login_required = True
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif (msg.type == WSMsgType.ERROR):
                self.request.app.logger.dubg('ws connection error: {}'.format(ws.exception()))
        return ws


class LogInView(web.View):
    async def post(self):
        data = await self.request.json()
        app = self.request.app
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return web.HTTPBadRequest()
        try:
            user = await app.objects.get(User, username=username, password=password)
        except User.DoesNotExist:
            return web.HTTPBadRequest('Wrong login or password, try again!')
        self.request.session['user'] = str(user.id)
        self.request.session['time'] = time()
        return web.HTTPOk()
