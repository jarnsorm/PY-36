from sqlalchemy import create_engine
# from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from db_shit.config import sync_settings

# async_engine = create_async_engine(async_settings.db_url)
sync_engine = create_engine(sync_settings.db_url)

# async_connection = async_sessionmaker(async_engine, autoflush=True)
sync_connection = sessionmaker(sync_engine, autoflush=True)