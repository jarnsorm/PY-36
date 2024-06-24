import datetime
from typing import Annotated
from db.data import sync_engine
from sqlalchemy import MetaData, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

metadata = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Documents(Base):
    __tablename__ = 'documents'

    id: Mapped[intpk]
    path: Mapped[str]
    date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class Documents_text(Base):
    __tablename__ = 'documents_text'

    id: Mapped[intpk]
    id_doc: Mapped[int] = mapped_column(ForeignKey('documents.id', ondelete='CASCADE'), unique=True)
    text: Mapped[str]


def init_models():
    # Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
