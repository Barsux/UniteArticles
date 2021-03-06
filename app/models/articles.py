from datetime import date
from pydantic import BaseModel, validator, ValidationError
from enum import Enum

class ArticleStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLICATED = "PUBLICATED"
    APPROWED = "APPROWED"
    DECLINED = "DECLINED"

class BaseMark(BaseModel):
    mark: int

    @validator('mark')
    def validate_mark(cls, mark):
        if mark not in range(0, 11):
            raise ValidationError
        return mark

class Mark(BaseMark):
    id: int
    article_id: int
    user_id: int

    class Config:
        orm_mode = True


class ArticleBase(BaseModel):
    creation_date: date
    last_used_date: date
    status: ArticleStatus
    summary_mark: int
    votes: int
    header: str
    text: str

class Article(ArticleBase):
    id: int
    class Config:
        orm_mode = True

class InputArticle(BaseModel):
    header: str
    text: str

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(ArticleBase):
    pass