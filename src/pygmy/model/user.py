from passlib.hash import bcrypt
from pygmy.database.base import Model
from pygmy.database.dbutil import dbconnection
from sqlalchemy.sql import func
from sqlalchemy import (
    Integer, Column, String, Boolean, DateTime)


class User(Model):
    __tablename__ = 'user'

    email = Column(String(120), primary_key=True)
    user_id = Column(Integer, autoincrement=True)
    f_name = Column(String(30), nullable=False)
    m_name = Column(String(30), default='')
    l_name = Column(String(30), nullable=False)
    username = Column(String(120), nullable=False)
    password = Column(String(300), nullable=False)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserManager:

    @dbconnection
    def add(self, db, email, f_name, l_name, password,
            username=None, m_name=None):
        if username is None:
            username = email
        password = bcrypt.encrypt(password)
        user = User(f_name=f_name, m_name=m_name, l_name=l_name,
                    email=email, password=password, username=username)
        db.add(user)
        db.commit()
        return user

    @dbconnection
    def find(self, db, email):
        user = db.query(User).filter(
                    User.email == email, User.is_deleted == False)
        if user.count() < 1:
            return None
        return user.one()

    @dbconnection
    def remove(self, db, email):
        user = self.find(email=email)
        user.is_deleted = True
        db.commit()




