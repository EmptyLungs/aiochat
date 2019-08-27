DATABASE = {
    'database': 'aiochat_db',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': '5432'
}

REDIS_CON = 'localhost', 6379

try:
    from local import *
except ImportError:
    pass
