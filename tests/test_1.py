import asyncio

import pytest
import os
from tests.config import SERVICE_URL
from tests.classes import Response
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
import requests
from db.models import Documents
from sqlalchemy import select, insert
from db.data import async_connection

client = AsyncClient(transport=ASGITransport(app))

file_name = "test_upload_image.jpg"
file_path = f"Documents/{file_name}"


async def doc_test_id(name):
    async with async_connection() as conn:
        stmt = select(Documents.id).filter(Documents.path == f"Documents/{name}")
        result = await conn.execute(stmt)
        doc_id = result.scalar()
        print(doc_id)
        return doc_id


@pytest.mark.asyncio
async def test_upload_valid_file():
    """Тест на загрузку файла с допустимым расширением"""
    with open(file_name, "wb") as f:
        f.write(b"test image content")
    with open(file_name, "rb") as f:
        response = await client.post(f"{SERVICE_URL}/upload_doc/", files={"file": (file_name, f, "image/jpeg")})
    assert response.status_code == 201
    assert response.json() == {'message': f'file "{file_name}" has been uploaded'}


@pytest.mark.asyncio
async def test_upload_invalid_file():
    """Тест на загрузку файла с недопустимым расширением"""
    with open("test_document.txt", "wb") as f:
        f.write(b"test document content")
    with open("test_document.txt", "rb") as f:
        response = await client.post(f"{SERVICE_URL}/upload_doc/", files={"file": ("test_document.txt", f, "text/plain")})
    assert response.status_code == 400
    assert response.json() == {'message': 'wrong format of file'}


@pytest.mark.asyncio
async def test_doc_delete():
    """Удаление файла"""
    # doc_id = await doc_test_id(file_name)
    doc_id = 80

    async with AsyncClient(app=app, base_url=f'{SERVICE_URL}') as clnt:
        response = await clnt.delete(f"/doc_delete/?doc_id={doc_id}")

    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    assert not os.path.exists(file_path), f"File {file_path} still exists after deletion"

    # async with async_connection() as conn:
    #     stmt = select(Documents).filter(Documents.id == doc_id)
    #     result = await conn.execute(stmt)
    #     document = result.scalar()
    #     assert document is None, f"Document with id {doc_id} still exists in the database"


