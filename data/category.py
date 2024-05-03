import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Category(SqlAlchemyBase):
    __tablename__ = 'category'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    product = orm.relationship("Products", back_populates='category')
