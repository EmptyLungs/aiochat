from time import time
import uuid

from aiohttp import web, WSMsgType
from peewee import JOIN_FULL

from models import Message, User, ChatRoom


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
    # login_required = True
    async def get(self):
        app = self.request.app
        user = self.request.user
        try:
            self.room = await app.objects.get(ChatRoom, id=self.request.match_info['slug'].lower())
        except ChatRoom.DoesNotExist:
            return web.HTTPNotFound()
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)

        last_messages = await app.objects.execute(
            Message.select(Message, User).join(User, JOIN_FULL). \
            where(Message.room == self.room).order_by(Message.created.desc()).limit(20))
        json_messages = list(map(Message.as_dict, last_messages))
        json_messages.reverse()
        await self.send_last_messages(json_messages, ws)

        if self.room.id not in app.ws_connections:
            app.ws_connections[self.room.id] = {}
        
        message = await app.objects.create(
            Message, room=self.room, user=None, text="@{} joined chat!".format(user.username if user else 'anon')
        )
        app.ws_connections[self.room.id][user.id if user else uuid.uuid4()] = ws
        await self.broadcast(message)

        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    text = msg.data.strip()
                    message = await app.objects.create(Message, room=self.room, user=user, text=text)
                    await self.broadcast(message)
            elif (msg.type == WSMsgType.ERROR):
                app.logger.dubg('ws connection error: {}'.format(ws.exception()))
        return ws

    async def broadcast(self, message):
        for conn in self.request.app.ws_connections[self.room.id].values():
            await conn.send_json(message.as_dict())
            # await conn.send_str(message.text)

    async def send_last_messages(self, messages, ws):
        for message in messages:
            await ws.send_json(message)

class LogInView(BaseView):
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
            return web.HTTPBadRequest()
        self.request.session['user'] = str(user.id)
        self.request.session['time'] = time()
        return web.json_response(user.as_dict())

class UserInfoView(BaseView):
    login_required = True
    async def get(self):
        return web.json_response(self.request.user.as_dict())


class RoomListView(BaseView):
    login_required = True
    async def get(self):
        # ohuet' mojno
        rooms = await self.request.app.objects.execute(ChatRoom.select(ChatRoom, User).join(User))
        resp = list(map(ChatRoom.as_dict, rooms))
        return web.json_response(resp)
