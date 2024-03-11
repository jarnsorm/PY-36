import datetime
from typing import Annotated
from db.data import async_engine
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


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sunc(Base.metadata.drop_all)
        await conn.run_sunc(Base.metadata.create_all)