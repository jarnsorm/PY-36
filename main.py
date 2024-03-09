import os
import shutil
import uvicorn

from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError

from celery_config import scan
from db_shit.data import async_connection
from db_shit.models import Documents, init_models, Documents_text

app = FastAPI()


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('index.html')


@app.post('/upload_doc')
async def upload_doc(file: UploadFile) -> dict:
    """загрузка файла в папку 'Documents', занесение данных о пути к файлу в БД"""
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        with open(f'Documents/{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        async with async_connection() as conn:
            doc = Documents(path=f'Documents/{file.filename}')
        conn.add(doc)
        await conn.commit()
        return {'message': f'file {file.filename} has been uploaded'}
    else:
        return {'message': 'wrong format of file'}


@app.delete('/doc_delete')
async def doc_delete(doc_id: int) -> dict:
    """удаление файла, удаление данных о нем из БД"""
    async with async_connection() as conn:
        try:
            query = Select(Documents.path).filter(Documents.id == doc_id)
            res = await conn.execute(query).one()
            os.remove(*res)
            await conn.query(Documents).filter(Documents.id == doc_id).delete()
            await conn.commit()
            return {'message': 'file has been deleted'}
        except Exception:
            return {'message': 'wrong id'}


@app.post('/doc_analyse')
async def doc_analyse(doc_id: int) -> dict:
    """занесение текста в БД"""
    try:
        async with async_connection() as conn:
            query = Select(Documents.path).filter(Documents.id == doc_id)
            result = await conn.execute(query)
            res = result.one()
            scan_text = scan.delay(*res)
            img_text = scan_text.get()
            doc_text = Documents_text(id_doc=doc_id, text=img_text)

        conn.add(doc_text)
        await conn.commit()
        return {'message': f'text has been added'}
    except (ValueError, IntegrityError):
        return {'message': 'wrong id'}


@app.get('/get_text')
async def get_text(doc_id: int) -> str | dict:
    """получение текста из БД"""
    async with async_connection() as conn:
        try:
            query = Select(Documents_text.text).filter(Documents_text.id_doc == doc_id)
            res = await conn.execute(query)
            result = res.one()
            return f'{result[0]}'
        except Exception:
            return {'message': 'wrong id'}


if __name__ == '__main__':
    init_models()
    uvicorn.run('main:app', reload=True)
