from celery import Celery
from PIL import Image
import pytesseract
from sqlalchemy import insert
from db.data import sync_connection
from db.models import Documents_text

celery = Celery('app.tasks', backend='rpc://', broker='pyamqp://guest@localhost//', include=['app.tasks'])
# celery -A app.tasks:celery worker --loglevel=INFO

celery.autodiscover_tasks()


@celery.task
def scan(image_path: str, doc_id: int):
    """Получение текста из изображения и сохранение его в базу данных"""
    try:
        with Image.open(image_path) as img:
            extracted_text = pytesseract.image_to_string(img)
            with sync_connection() as conn:
                stmt = insert(Documents_text).values(id_doc=doc_id, text=extracted_text)
                conn.execute(stmt)
                conn.commit()
        return 'bitsh'
    except Exception as e:
        print(f"Ошибка при сканировании изображения: {e}")