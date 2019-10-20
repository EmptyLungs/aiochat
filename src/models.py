from peewee import CharField, TextField, ForeignKeyField

from db import BaseModel

class User(BaseModel):
    username = CharField(unique=True, index=True, null=False, max_length=20)
    # plaintext password yaaa
    # TODO: passlib.hash - sha256_crypt.verify(password, hash)
    password = CharField(max_length=20)

    def as_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }


class ChatRoom(BaseModel):
    name = CharField(max_length=20, unique=True)
    owner = ForeignKeyField(rel_model=User, related_name='owner', on_delete='SET NULL')

    @classmethod
    async def all_messages(cls, objects):
        return await objects.prefetch(self.messages, User.select())

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner": self.owner.as_dict()
        }


class Message(BaseModel):
    text = TextField()
    user = ForeignKeyField(rel_model=User, related_name='messages', on_delete='CASCADE', null=True)
    room = ForeignKeyField(rel_model=ChatRoom, related_name='messages', on_delete='CASCADE')

    def as_dict(self):
        return {
            "text": self.text, "created": self.created.isoformat(),
            "user": {"username": self.user.username, "id": self.user.id} if self.user else None
        }
