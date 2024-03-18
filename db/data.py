from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from db.config import async_settings, sync_settings

async_engine = create_async_engine(async_settings.db_url)
sync_engine = create_engine(sync_settings.db_url)
async_connection = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
sync_connection = sessionmaker(sync_engine)
