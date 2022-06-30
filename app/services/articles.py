from typing import List, Optional

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session

from app import tables
from app.database import get_session
from app.models.articles import ArticleStatus, ArticleCreate, ArticleUpdate

class ArticlesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _get_by_id(self, article_id: int):
        operation = (
            self.session
                .query(tables.Article)
                .filter_by(id=article_id)
                .first()
        )
        if not operation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return operation

    def get_list(self, status: Optional[ArticleStatus] = None) -> List[tables.Article]:
        query = self.session.query(tables.Article)
        if status:
            query = query.filter_by(status=status)
        articles = query.all()
        return articles

    def create_article(self, article_data: ArticleCreate) -> tables.Article:
        article = tables.Article(**article_data.dict())
        self.session.add(article)
        self.session.commit()
        return article

    def get_article(self, article_id: int) -> tables.Article:
        return self._get_by_id(article_id)

    def update_article(self, article_id: int, article_data: ArticleUpdate, status: Optional[ArticleStatus] = None) -> tables.Article:
        article = self._get_by_id(article_id)
        if status:
            article.status = status
        for field, value in article_data:
            setattr(article, field, value)
        self.session.commit()
        return article

    def delete_article(self, article_id: int):
        article = self._get_by_id(article_id)
        self.session.delete(article)
        self.session.commit()