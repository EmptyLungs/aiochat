from datetime import datetime

from peewee import Model, DateTimeField
from peewee_async import PostgresqlDatabase

from settings import DATABASE

database = PostgresqlDatabase(**DATABASE)

class BaseModel(Model):
    created = DateTimeField(formats='%Y-%m-%d %H:%M:%S', default=datetime.utcnow)
    updated = DateTimeField(formats='%Y-%m-%d %H:%M:%S', default=datetime.utcnow)

    @classmethod
    def update(cls, __data=None, **update):
        update['updated'] = datetime.utcnow()
        return super(BaseModel, cls).update(__data, **update)

    def __repr__(self):
        return "{} instance, id={}".format(self.__class__.__name__, self.id)

    class Meta:
        database = database
