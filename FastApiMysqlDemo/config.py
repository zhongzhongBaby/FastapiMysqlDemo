from pydantic import BaseSettings
from functools import lru_cache


@lru_cache()
def get_settings():
    return Settings(_env_file='prod.env')


class Settings(BaseSettings):
    app_name: str = "FastApiMysqlDemo"
    admin_email: str = "844383583@qq.com"
    database: dict = {
        "url": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "12346",
        "database_name": "demo"
    }

    class Config:
        env_file = "prod.env"
