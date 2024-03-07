import shutil, os, uvicorn, pytesseract
from PIL import Image
from sqlalchemy import Select
from db_shit.models import Documents, create_tables, Documents_text
from db_shit.data import sync_connection
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from celery import Celery


app = FastAPI()
celery = Celery('tasks', broker='pyamqp://guest@localhost//')


@celery.task
def scan(image: str) -> str:
    img = Image.open(image)
    extr_text = pytesseract.image_to_string(img)
    return extr_text
    pass


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('index.html')


@app.post('/upload_doc')
def upload_doc(file: UploadFile) -> dict:
    """загрузка файла в папку 'Documents', занесение данных о пути к файлу в БД"""
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        with open(f'Documents/{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        with sync_connection() as conn:
            doc = Documents(path=f'Documents/{file.filename}')
        conn.add(doc)
        conn.commit()
        return {'massage': f'file {file.filename} has been uploaded'}
    else:
        return {'massage': 'wrong format of file'}


@app.delete('/doc_delete')
def doc_delete(file_id: int) -> dict:
    """удаление файла, удаление данных о нем из БД"""
    with sync_connection() as conn:
        try:
            query = Select(Documents.path).filter(Documents.id == file_id)
            res = conn.execute(query).one()
            os.remove(*res)
            conn.query(Documents).filter(Documents.id == file_id).delete()
            conn.commit()
            return {'massage': 'file has been deleted'}
        except Exception:
            return {'massage': 'wrong id'}


@app.get('/doc_analyse')
async  def doc_analyse(file_id: int) -> dict[str, str]:
    """получение текста из картинки, занесение текста в БД"""
    try:
        with sync_connection() as conn:
            query = Select(Documents.path).filter(Documents.id == file_id)
            res = conn.execute(query).one()
            img_text = scan(*res)
            doc_text = Documents_text(id_doc=file_id, text=f'{img_text}')
            print(img_text)
        conn.add(doc_text)
        conn.commit()
        return {'massage': f'text has been added'}
    except Exception:
        return {'massage': 'wrong id'}


@app.get('/get_text')
def get_text(file_id: int) -> str | dict[str, str]:
    """получение текста из БД"""
    with sync_connection() as conn:
        try:
            query = Select(Documents_text.text).filter(Documents_text.id_doc == file_id)
            res = conn.execute(query).one()
            return f'{res}'
        except Exception:
            return {'massage': 'wrong id'}
    pass


if __name__ == '__main__':
    create_tables()
    uvicorn.run('main:app', reload=True)