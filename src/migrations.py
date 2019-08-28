import asyncio

import peewee_async

from models import User, Message
from db import database
from settings import DATABASE

database.init(**DATABASE)
manager = peewee_async.Manager(database)

with manager.allow_sync():
    User.create_table(True)
    Message.create_table(True)
    
    for username in ['User1', 'User2', 'User3']:
        User.create(username=username, password='123')