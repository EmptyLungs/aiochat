import asyncio

import peewee_async

from models import User, Message, ChatRoom
from db import database
from settings import DATABASE

database.init(**DATABASE)
manager = peewee_async.Manager(database)

with manager.allow_sync():
    User.create_table(True)
    Message.create_table(True)
    ChatRoom.create_table(True)
    
    for username in ['User1', 'User2', 'User3']:
        try:
            User.create(username=username, password='123')
        except:
            pass
    default_user = User.get(User.id == 1)
    for room in ['flood', 'nsfw', 'music']:
        ChatRoom.create(name=room, owner=default_user)
