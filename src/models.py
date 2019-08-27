from peewee import CharField

from db import BaseModel

class User(BaseModel):
    username = CharField(unique=True, index=True, null=False, max_length=20)
    # plaintext password yaaa
    # TODO: passlib.hash - sha256_crypt.verify(password, hash)
    password = CharField(max_length=20)
