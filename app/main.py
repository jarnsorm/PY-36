import os
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.tasks import scan
from db.data import async_connection
from db.models import Documents, init_models, Documents_text

app = FastAPI()


async def doc_id_to_path(doc_id: int) -> str:
    async with async_connection() as conn:
        stmt = select(Documents.path).filter(Documents.id == doc_id)
        result = await conn.execute(stmt)
    return result.scalar()


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('app/index.html')


@app.post('/upload_doc/')
async def upload_doc(file: UploadFile) -> dict:
    """загрузка файла в папку 'Documents', занесение данных о пути к файлу в БД"""
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        try:
            async with aiofiles.open(f'Documents/{file.filename}', 'wb') as buffer:
                await buffer.write(await file.read())
            async with async_connection() as conn:
                stmt = insert(Documents).values(path=f'Documents/{file.filename}')
                await conn.execute(stmt)
                await conn.commit()
            return {'message': f'file {file.filename} has been uploaded'}
        except Exception as e:
            print(e)
            return {'message': f'An error occurred: {str(e)}'}
    else:
        return {'message': 'wrong format of file'}


@app.delete('/doc_delete/')
async def doc_delete(doc_id: int) -> dict:
    """удаление файла, удаление данных о нем из БД"""
    try:
        res = await doc_id_to_path(doc_id)
        os.remove(res)
        async with async_connection() as conn:
            obj = await conn.get(Documents, doc_id)
            await conn.delete(obj)
            await conn.commit()
        return {'message': 'file has been deleted'}
    except (ValueError, IntegrityError):
        return {'message': 'wrong id'}


@app.post('/doc_analyse/')
async def doc_analyse(doc_id: int) -> dict:
    """занесение текста в БД"""
    try:
        res = await doc_id_to_path(doc_id)
        scan.delay(res, doc_id)
        return {'message': 'text has been added'}
    except IntegrityError:
        return {'message': 'wrong id'}


@app.get('/get_text/')
async def get_text(doc_id: int) -> str | dict:
    """получение текста из БД"""

    try:
        async with async_connection() as conn:
            stmt = select(Documents_text.text).filter(Documents_text.id == doc_id)
            res = await conn.execute(stmt)
            result = res.scalar()
        return f'{result}'
    except (ValueError, IntegrityError):
        return {'message': 'wrong id'}


if __name__ == '__main__':
    init_models()
    uvicorn.run('main:app', host="0.0.0.0", reload=True)