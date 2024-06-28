import asyncio
import pytest
from db.models import Base
from db.data import sync_engine


@pytest.fixture(scope='function')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Создание ББД для тестов. Удаление БД после прохождения тестов"""
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    # yield
    # Base.metadata.drop_all(sync_engine)
    # Base.metadata.create_all(sync_engine)


@pytest.fixture()
def documents():
    return [
        "Documents/file_1.png",
        "Documents/file_2.png",
        "Documents/file_3.png",
        "Documents/file_4.png"
    ]