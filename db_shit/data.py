from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import settings

engine = create_engine(settings.db_url)

connection = sessionmaker(engine, autoflush=True)