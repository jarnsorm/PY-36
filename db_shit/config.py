from celery import Celery
from pydantic_settings import BaseSettings, SettingsConfigDict


# class AsyncUrlSettings(BaseSettings):
#     DB_HOST: str
#     DB_PORT: int
#     DB_NAME: str
#     DB_USER: str
#     DB_PASS: str
#
#     @property
#     def db_url(self):
#         return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT} /{self.DB_NAME}'
#
#     model_config = SettingsConfigDict(env_file='.env')


class SyncUrlSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    @property
    def db_url(self):
        return f'postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT} /{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env')


# async_settings = AsyncUrlSettings()
sync_settings = SyncUrlSettings()

celery = Celery('tasks', broker='pyamqp://guest@localhost//')
