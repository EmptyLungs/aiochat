from peewee import CharField, TextField, ForeignKeyField

from db import BaseModel

class User(BaseModel):
    username = CharField(unique=True, index=True, null=False, max_length=20)
    # plaintext password yaaa
    # TODO: passlib.hash - sha256_crypt.verify(password, hash)
    password = CharField(max_length=20)


class Message(BaseModel):
    text = TextField()
    user = ForeignKeyField(rel_model=User, related_name='messages', on_delete='CASCADE')
