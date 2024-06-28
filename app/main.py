import os
import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, status, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from app.tasks import scan
from db.data import async_connection
from db.models import Documents, init_models, Documents_text

app = FastAPI()


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('app/index.html')


@app.post('/upload_doc/')
async def upload_doc(file: UploadFile) -> JSONResponse:
    """Загрузка файла в папку 'Documents', занесение данных о пути к файлу в БД"""
    try:
        if not file.filename.endswith(('.png', '.jpg', '.jpeg')):
            return JSONResponse(content={'message': 'wrong format of file'},
                                status_code=400)
        file_path = f'Documents/{file.filename}'
        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)

        async with async_connection() as conn:
            stmt = insert(Documents).values(path=file_path)
            await conn.execute(stmt)
            await conn.commit()

        return JSONResponse(content={'message': f'file "{file.filename}" has been uploaded'},
                            status_code=201)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return JSONResponse(content={'message': f'An error occurred: {str(e)}'},
                            status_code=500)


async def doc_id_to_path(doc_id: int) -> str:
    async with async_connection() as conn:
        async with conn.begin():
            stmt = select(Documents.path).filter(Documents.id == doc_id)
            result = await conn.execute(stmt)
            path = result.scalar()
            if not path:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with id={doc_id} not found")
            return path


@app.delete('/doc_delete/')
async def doc_delete(doc_id: int) -> JSONResponse:
    """Удаление файла и данных о нем из БД"""
    try:
        # file_path = await doc_id_to_path(doc_id)
        file_path = "Documents/test_upload_image.jpg"
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found at {file_path}")
        async with async_connection() as session:
            obj = await session.get(Documents, doc_id)
            if obj is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Document with id={doc_id} not found")
            await session.delete(obj)
            await session.delete(Documents, doc_id)
            await session.commit()

        return JSONResponse(content={'message': 'File and data have been deleted'},
                            status_code=status.HTTP_200_OK)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"An error occurred in 'doc_delete': {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post('/doc_analyse/')
async def doc_analyse(doc_id: int) -> JSONResponse:
    """Занесение текста в БД"""
    try:
        res = await doc_id_to_path(doc_id)
        scan.delay(res, doc_id)
        return JSONResponse(content={'message': 'text has been added'},
                            status_code=status.HTTP_200_OK)
    except ValueError:
        return JSONResponse(content={'message': 'wrong id'},
                            status_code=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        return JSONResponse(content={'message': 'database integrity error'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={'message': f'An error occurred: {str(e)}'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get('/get_text/')
async def get_text(doc_id: int) -> JSONResponse:
    """Получение текста из БД"""
    try:
        async with async_connection() as conn:
            stmt = select(Documents_text.text).where(Documents_text.id == doc_id)
            res = await conn.execute(stmt)
            result = res.scalar()
            if result is None:
                raise ValueError("Document text not found")
        return JSONResponse(content={'text': result},
                            status_code=status.HTTP_200_OK)
    except ValueError:
        return JSONResponse(content={'message': 'wrong id'},
                            status_code=status.HTTP_404_NOT_FOUND)
    except IntegrityError:
        return JSONResponse(content={'message': 'database integrity error'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return JSONResponse(content={'message': f'An error occurred: {str(e)}'},
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


if __name__ == '__main__':
    init_models()
    uvicorn.run('main:app', host="0.0.0.0", reload=True)