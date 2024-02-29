import datetime
from typing import Annotated

from sqlalchemy import MetaData
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

metadata = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]


class Base(DeclarativeBase):
    pass


class Documents(Base):
    __tablename__ = 'documents'

    id: Mapped[intpk]
    psth: Mapped[str]
    date: Mapped[datetime.datetime.utcnow]


class Documents_text(Base):
    __tablename__ = 'documents_text'

    id: Mapped[intpk]
    id_doc: Mapped[int] = mapped_column(ForeignKey=Documents.id)
    text: Mapped[str]