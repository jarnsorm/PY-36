from celery import Celery
from PIL import Image
import pytesseract

c_app = Celery('tasks', backend='rpc://', broker='pyamqp://guest@localhost//')


@c_app.task
def scan(image: str) -> str:
    """получение текста из картинки"""
    img = Image.open(image)
    extr_text = pytesseract.image_to_string(img)
    return extr_text

# celery -A for_celery.celery_config worker --loglevel=INFO