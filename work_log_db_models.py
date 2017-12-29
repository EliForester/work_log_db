from peewee import Model, DateField, CharField, TextField, IntegerField, \
    OperationalError
from playhouse.sqlite_ext import SqliteExtDatabase
from datetime import datetime

db = SqliteExtDatabase('work_log.db')


class BaseModel(Model):
    class Meta:
        database = db


class Entry(BaseModel):
    date = DateField(default=datetime.now)
    user = CharField()
    task_name = TextField()
    time_spent = IntegerField()
    notes = TextField()


if __name__ == '__main__':
    try:
        Entry.create_table()
    except OperationalError:
        print('Entry table already exists.')
