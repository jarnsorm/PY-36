import shutil, os, uvicorn
from sqlalchemy import Select
from db_shit.models import Documents, create_tables, Documents_text
from db_shit.data import sync_connection
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse


app = FastAPI()


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('index.html')


@app.post('/upload_doc')
def upload_doc(file: UploadFile):
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
def doc_delete(file_id: int):
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
def doc_analyse(file_id: int):
    """получение текста из картинки, занесение текста в БД"""
    pass


@app.get('/get_text')
def get_text(file_id: int):
    """получение текста из БД"""
    with sync_connection() as conn:
        try:
            query = Select(Documents_text.text).filter(Documents.id == file_id)
            res = conn.execute(query).one()
            return {'massage': f'{res}'}
        except Exception:
            return {'massage': 'wrong id'}
    pass


if __name__ == '__main__':
    create_tables()
    uvicorn.run('main:app', reload=True)