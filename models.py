from datetime import datetime
from sqlalchemy import inspect
from weakref import WeakValueDictionary
from sqlalchemy.orm import aliased
from app import db
import uuid


class MetaBaseModel(db.Model.__class__):
    """ Define a metaclass for the BaseModel to implement `__getitem__` for managing aliases """

    def __init__(cls, *args):
        super().__init__(*args)
        cls.aliases = WeakValueDictionary()

    def __getitem__(cls, key):
        try:
            alias = cls.aliases[key]
        except KeyError:
            alias = aliased(cls)
            cls.aliases[key] = alias
        return alias

class BaseModel:
    print_filter = ()

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            {column: value for column, value in self._to_dict().items() if column not in self.print_filter},
        )

    to_json_filter = ()

    def json(self):
        return {
            column: self._format_value(value)
            for column, value in self._to_dict().items()
            if column not in self.to_json_filter
        }

    to_json_datetime_format = "%Y-%m-%dT%H:%M:%S"

    def _format_value(self, value):
        """ Format value depending on type """
        if isinstance(value, datetime):
            return value.strftime(self.to_json_datetime_format)
        if isinstance(value, uuid.UUID):
            return str(value)
        return value

    def _to_dict(self):
        return {column.key: getattr(self, column.key) for column in inspect(self.__class__).attrs}

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

class User(db.Model, BaseModel, metaclass=MetaBaseModel):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)