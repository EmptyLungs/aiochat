DATABASE = {
    'database': 'aiochat_db',
    'user': '',
    'password': '',
    'host': 'localhost',
    'port': '5432'
}

try:
    from local import *
except ImportError:
    pass
