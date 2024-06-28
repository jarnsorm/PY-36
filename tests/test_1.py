import pytest
import os
from tests.config import SERVICE_URL
from fastapi.testclient import TestClient
from app.main import app
from db.models import Documents, Base
from sqlalchemy import select, insert, func
from db.data import sync_connection, sync_engine, async_connection

client = TestClient(app)

file_name = "test_upload_image.jpg"
file_path = f"Documents/{file_name}"


def test_db_connection(documents):
    with sync_connection() as conn:
        with conn.begin():
            conn.execute(insert(Documents).values([{"path": path} for path in documents]))
            conn.commit()
        result = conn.execute(select(func.count(Documents.id)))
        count = result.scalar()
        assert count == len(documents)


def test_upload_valid_file():
    """Тест на загрузку файла с допустимым расширением"""
    with open(file_name, "wb") as f:
        f.write(b"test image content")
    with client:
        with open(file_name, "rb") as f:
            response = client.post(f"{SERVICE_URL}/upload_doc/", files={"file": (file_name, f, "image/jpeg")})
        assert response.status_code == 201
        assert response.json() == {'message': f'file "{file_name}" has been uploaded'}
    os.remove(file_name)


def test_upload_invalid_file():
    """Тест на загрузку файла с недопустимым расширением"""
    with open("test_document.txt", "wb") as f:
        f.write(b"test document content")
    with open("test_document.txt", "rb") as f:
        response = client.post(f"{SERVICE_URL}/upload_doc/", files={"file": ("test_document.txt", f, "text/plain")})
    assert response.status_code == 400
    assert response.json() == {'message': 'wrong format of file'}
    os.remove("test_document.txt")


def test_doc_delete():
    with client:
        response = client.delete(f"{SERVICE_URL}/doc_delete/?doc_id=5")
        assert response.status_code == 200
        assert response.json() == {'message': 'File and data have been deleted'}
    # with async_connection() as session:
    #     result = session.execute(select(Documents).filter(Documents.id == 5))
    #     deleted_doc = result.scalar()
    #     assert deleted_doc is None
    # assert not os.path.exists("test_file.jpg")

