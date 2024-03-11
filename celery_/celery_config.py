from celery import Celery
from PIL import Image
import pytesseract

celery = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost//')


@celery.task
def scan(image: str) -> str:
    """получение текста из картинки"""
    img = Image.open(image)
    extr_text = pytesseract.image_to_string(img)
    return extr_text

# celery -A celery_.celery_config worker --loglevel=INFO