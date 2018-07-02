import datetime

from passlib.hash import bcrypt
from sqlalchemy import Integer, Column, String, Boolean, DateTime

from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection, utcnow


class User(Model):
    __tablename__ = 'user'

    email = Column(String(120), unique=True, index=True)
    id = Column(Integer, autoincrement=True, primary_key=True)
    f_name = Column(String(30), nullable=False)
    m_name = Column(String(30), default='')
    l_name = Column(String(30), nullable=False)
    password = Column(String(300), nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=False), server_default=utcnow())
    updated_at = Column(DateTime(timezone=False), onupdate=utcnow())


class UserManager:
    # TODO 1: make an abstract class for managers
    # TODO 2: A seperate directory for all ABC
    # TODO 3: Make attr of Model accessible from manager class
    # Override __getattr__ and __setattr__
    def __init__(self, user=None):
        self.user = user

    @staticmethod
    def build_query(**kwargs):
        query_dict = dict()
        if kwargs.get('email'):
            query_dict['email'] = kwargs.get('email')
        if kwargs.get('id'):
            query_dict['id'] = kwargs.get('id')
        return query_dict

    @dbconnection
    def get(self, db, _id):
        user_obj = db.query(User).filter_by(id=_id)
        if user_obj.count() < 1:
            return None
        self.user = user_obj.one()
        return self.user

    @dbconnection
    def get_by_email(self, db, email):
        user_obj = db.query(User).filter_by(email=email)
        if user_obj.count() < 1:
            return None
        self.user = user_obj.one()
        return self.user

    @dbconnection
    def add(self, db, email, f_name, l_name, password, m_name=None):
        password = bcrypt.encrypt(password)
        insert_values = dict(f_name=f_name, m_name=m_name, l_name=l_name,
                             email=email, password=password)
        if db.bind.name == 'mysql':
            insert_values['created_at'] = datetime.datetime.utcnow()
            insert_values['updated_at'] = datetime.datetime.utcnow()
        self.user = User(**insert_values)
        db.add(self.user)
        db.commit()
        return self.user

    @dbconnection
    def find(self, db, email, **kwargs):
        kwargs['email'] = email
        query_dict = self.build_query(**kwargs)
        user_obj = db.query(User).filter_by(**query_dict)
        if user_obj.count() < 1:
            return None
        self.user = user_obj.one()
        return self.user

    @dbconnection
    def remove(self, db, email):
        user = self.find(email=email)
        user.is_deleted = True
        db.commit()
