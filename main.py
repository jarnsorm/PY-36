import shutil

from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Annotated
import uvicorn
import enum

app = FastAPI()


# class PicType(enum.Enum):
#     """доступные форматы для загрузки"""
#     jpeg = 'jpeg'
#     gif = 'gif'
#     png = 'png'


# class Image(BaseModel):
#     url: HttpUrl
#     name: Annotated[str, Query(pattern='.jpeg')]


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('index.html')


@app.post('/upload_doc')
async def upload_file(file: UploadFile):
    with open(f'Documents/{file.filename}', 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {'filename': file.filename}


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)