from db_shit.data import sync_connection, sync_engine
from db_shit.models import Base, Documents


def create_tables():
    Base.metadata.create_all(sync_engine)


def drop_tables():
    Base.metadata.drop_all(sync_engine)


def doc_add(filename):
    with sync_connection() as conn:
        doc = Documents(
            path=f'Documents/{filename}',
        )
    conn.add(doc)
    conn.commit()


def doc_del(id: int):
    with sync_connection() as conn:
        conn.query(Documents).filter(Documents.id == id).delete()
        conn.commit()


