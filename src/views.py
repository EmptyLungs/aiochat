from aiohttp import web, WSMsgType
from models import Message, User
from time import time


class Test(web.View):
    async def get(self):
        return web.json_response({"data": {"message": "Hello World!"}})


class WebSocket(web.View):
    async def get(self):
        #if self.request.user == None:
        #    return web.HTTPUnauthorized()
        print(self.request.user.username)
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    print('connection closed')
                    await ws.close()
                else:
                    await ws.send_str(msg.data + '/answer')
            elif (msg.type == WSMsgType.ERROR):
                print('ws connection error: {}'.format(ws.exception()))
        return ws


class LogInView(web.View):
    async def post(self):
        data = await self.request.json()
        app = self.request.app
        username = data.get('username')
        password = data.get('password')
        print(username,password)
        if not username or not password:
            return web.HTTPBadRequest()
        try:
            user = await app.objects.get(User, username=username, password=password)
        except User.DoesNotExist:
            return web.HTTPBadRequest('Wrong login or password, try again!')
        self.request.session['user'] = str(user.id)
        self.request.session['time'] = time()
        return web.HTTPOk()
