import asyncio

import pytest
import os
from tests.config import SERVICE_URL
from tests.classes import Response
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
import requests
from db.models import Documents, Base
from sqlalchemy import select, insert, func
from db.data import async_connection, sync_engine

client = TestClient(app)
a_client = AsyncClient(transport=ASGITransport(app=app), base_url=SERVICE_URL)
a_client.get_io_loop = asyncio.get_running_loop

file_name = "test_upload_image.jpg"
file_path = f"Documents/{file_name}"


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url=SERVICE_URL) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Создание ББД для тестов. Удаление БД после прохождения тестов"""
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)


@pytest.fixture()
def documents():
    return [
        "Documents/file_1.png",
        "Documents/file_2.png",
        "Documents/file_3.png",
        "Documents/file_4.png"
    ]


class TestDocuments:
    @pytest.mark.asyncio
    async def test_db_connection(self, documents):
        async with async_connection() as conn:
            async with conn.begin():
                await conn.execute(insert(Documents).values([{"path": path} for path in documents]))
            await conn.commit()
            result = await conn.execute(select(func.count(Documents.id)))
            count = result.scalar()
            assert count == len(documents)

    @pytest.mark.skip("attached to a different loop")
    @pytest.mark.asyncio
    async def test_upload_valid_file(self):
        """Тест на загрузку файла с допустимым расширением"""
        with open(file_name, "wb") as f:
            f.write(b"test image content")
        async with a_client as ac:
            with open(file_name, "rb") as f:
                response = await ac.post("/upload_doc/", files={"file": (file_name, f, "image/jpeg")})
            assert response.status_code == 201
            assert response.json() == {'message': f'file "{file_name}" has been uploaded'}
        os.remove(file_name)

    def test_upload_invalid_file(self):
        """Тест на загрузку файла с недопустимым расширением"""
        with open("test_document.txt", "wb") as f:
            f.write(b"test document content")
        with open("test_document.txt", "rb") as f:
            response = client.post(
                f"{SERVICE_URL}/upload_doc/", files={"file": ("test_document.txt", f, "text/plain")}
                )
        assert response.status_code == 400
        assert response.json() == {'message': 'wrong format of file'}
        os.remove("test_document.txt")

    @pytest.mark.skip("attached to a different loop")
    @pytest.mark.asyncio
    async def test_doc_delete(self):
        async with AsyncClient(app=app, base_url=SERVICE_URL) as ac:
            response = await ac.delete(f"/doc_delete/?doc_id=2")
            assert response.status_code == 200
            assert response.json() == {'message': 'File and data have been deleted'}

        # Verify the document is deleted
        async with async_connection() as session:
            result = await session.execute(select(Documents).filter(Documents.id == 2))
            deleted_doc = result.scalar()
            assert deleted_doc is None

        # Verify the file is deleted
        assert not os.path.exists("test_file.jpg")



