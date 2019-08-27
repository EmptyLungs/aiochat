import asyncio

from server import start_app
from models import User

loop = asyncio.get_event_loop()
server_gen, handler, app = loop.run_until_complete(start_app(loop))

with app.objects.allow_sync():
    User.create_table(True)
    
    for username in ['User1', 'User2', 'User3']:
        try:
            User.create(username=user, password='123')
        except:
            # meh
            pass