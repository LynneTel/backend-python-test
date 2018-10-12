from sqlalchemy import Column, Integer, String, ForeignKey, inspect
from alayatodo import db


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255), unique=True)

    def __init__(self, id=None, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password

    # def __repr__(self):
    #     return '<User %r>' % self.username


class Todo(db.Model):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String(255))
    completed = Column(Integer)

    def __init__(self, user_id=None, description=None, completed=None):
        self.user_id = user_id
        self.description = description
        self.completed = completed

    # def __repr__(self):
    #     return '<Description %r>' % self.description


def object_as_dict(obj):
    return {c.key:getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
