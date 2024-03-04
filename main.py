import shutil
from db_shit.db_methods import create_tables, doc_add, doc_del
from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()



@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('index.html')


@app.post('/upload_doc')
def upload_file(file: UploadFile):
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        with open(f'Documents/{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        doc_add(file.filename)
        return {f'Файл {file.filename} сохранен'}
    else:
        return {'massage': 'wrong file.format'}


@app.delete('/doc_delete')
def delete_file(file_id: int):
    doc_del(file_id)


if __name__ == '__main__':
    create_tables()
    uvicorn.run('main:app', reload=True)