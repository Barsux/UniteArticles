import os

from pydantic import BaseSettings

databasedir = os.getcwd()
databasedir = databasedir[:databasedir.rfind('\\')]

class Settings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = 8080
    database_url: str = f"sqlite:///{databasedir}/database.sqlite3"
    #database_url: str = f"sqlite:///./database.sqlite3"

settings = Settings(
    _env_file='.env',
    _env_file_encoding="utf-8",
)