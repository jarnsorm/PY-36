from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from db.config import async_settings

async_engine = create_async_engine(async_settings.db_url)

async_connection = async_sessionmaker(async_engine)
