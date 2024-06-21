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


async def doc_id_to_path(doc_id: int) -> str:
    print("starting 'doc_id_to_path'")
    try:
        async with async_connection() as conn:
            stmt = select(Documents.path).filter(Documents.id == doc_id)
            result = await conn.execute(stmt)
            path = result.scalar()
            if not path:
                raise ValueError(f"File path not found for doc_id={doc_id}")
            return path
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


@app.get('/')
def root():
    """вывод приветственной страницы"""
    return FileResponse('app/index.html')


@app.post('/upload_doc/')
async def upload_doc(file: UploadFile) -> JSONResponse:
    """Загрузка файла в папку 'Documents', занесение данных о пути к файлу в БД"""
    if file.filename.endswith(('.png', '.jpg', '.jpeg')):
        try:
            async with aiofiles.open(f'Documents/{file.filename}', 'wb') as buffer:
                await buffer.write(await file.read())
            async with async_connection() as conn:
                stmt = insert(Documents).values(path=f'Documents/{file.filename}')
                await conn.execute(stmt)
                await conn.commit()
            return JSONResponse(content={'message': f'file "{file.filename}" has been uploaded'},
                                status_code=status.HTTP_201_CREATED)
        except Exception as e:
            return JSONResponse(content={'message': f'An error occurred: {str(e)}'},
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JSONResponse(content={'message': 'wrong format of file'},
                            status_code=status.HTTP_400_BAD_REQUEST)


@app.delete('/doc_delete/')
async def doc_delete(doc_id: int) -> JSONResponse:
    """Удаление файла и данных о нем из БД"""
    try:
        file_path = await doc_id_to_path(doc_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found at {file_path}")
        async with async_connection() as conn:
            obj = await conn.get(Documents, doc_id)
            if obj is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document with id={doc_id} not found")
            await conn.delete(obj)
            await conn.commit()
        return JSONResponse(content={'message': 'File and data have been deleted'},
                            status_code=status.HTTP_200_OK)
    except HTTPException as http_exc:
        raise http_exc
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f"Document not found")


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
            stmt = select(Documents_text.c.text).where(Documents_text.c.id == doc_id)
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