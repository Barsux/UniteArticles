import os

from pydantic import BaseSettings

databasedir = os.getcwd()
databasedir = databasedir[:databasedir.rfind('\\')]

class Settings(BaseSettings):
    server_host: str = "127.0.0.1"
    server_port: int = 80
    database_url: str = f"sqlite:///{databasedir}/database.sqlite3"
    #database_url: str = f"sqlite:///./database.sqlite3"
    ssl_keyfile: str = None
    ssl_certfile: str = None
    jwt_secret: str = "gUD1MiVHuNPdTrdAX0Qu_pNkgcRJ3Ni2selzPpjPULc"
    jwt_algorithm: str = "HS256"
    jwt_ttl: int = 3600

settings = Settings(
    _env_file='.env',
    _env_file_encoding="utf-8",
)
