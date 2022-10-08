import sqlalchemy as sa
from sqlalchemy import orm
from datetime import date
from db_session import SqlAlchemyBase


class Vines(SqlAlchemyBase):
    """Таблица вин"""
    __tablename__ = 'vines'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = sa.Column(sa.String)
    vine_type = sa.Column(sa.String)
    variety = sa.Column(sa.String)
    place = sa.Column(sa.String)
    photo_path = sa.Column(sa.String, default=None)
    barcode = sa.Column(sa.Integer, default=None)
    comment = orm.relation('Comments', lazy='dynamic', viewonly=True)


class Comments(SqlAlchemyBase):
    """Таблица комментариев"""
    __tablename__ = 'comments'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, nullable=False)
    vine_id = sa.Column(sa.Integer, sa.ForeignKey(Vines.id))
    chat_id = sa.Column(sa.Integer)
    date = sa.Column(sa.Date, default=date.today())
    mark = sa.Column(sa.Integer)
    price = sa.Column(sa.Integer)
    commentary = sa.Column(sa.Text)
    vine = orm.relation('Vines')
