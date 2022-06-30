from datetime import date
from pydantic import BaseModel
from enum import Enum

class ArticleStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLICATED = "PUBLICATED"
    APPROWED = "APPROWED"
    DECLINED = "DECLINED"

class ArticleBase(BaseModel):
    creation_date: date
    last_used_date: date
    status: ArticleStatus
    header: str
    text: str

class Article(ArticleBase):
    id: int
    class Config:
        orm_mode = True



class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(ArticleBase):
    pass