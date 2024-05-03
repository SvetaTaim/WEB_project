import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Basket(SqlAlchemyBase):
    __tablename__ = 'baskets'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    composition = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey("users.id"))
    pay = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    user = orm.relationship('User')