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
from app.models.auth import User, UserRole, BaseComment, CommentStatus

class ArticlesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def raise_400_with_text(self, text):
        exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=text,
            headers={'WWW-Authentificate': 'Bearer'}
        )
        raise exception from None

    def raise_401_with_text(self, text):
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=text,
            headers={'WWW-Authentificate': 'Bearer'}
        )
        raise exception from None

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

    def get_list(self, user: User, only_mine: bool = False, status: Optional[ArticleStatus] = None) -> List[tables.Article]:
        query = self.session.query(tables.Article)
        if status:
            query = query.filter_by(status=status)
        if only_mine:
            query = query.filter_by(user_id=user.id)
        articles = query.all()
        return articles

    def create_article(self, user: User, article_data: ArticleCreate) -> tables.Article:
        article = tables.Article(**article_data.dict())
        article.user_id = user.id
        if article.status != ArticleStatus.DRAFT:
            self.raise_400_with_text("Not correct status")
        if user.role not in [UserRole.ADMIN, UserRole.WRITER]:
            self.raise_401_with_text("You can't publish articles")
        self.session.add(article)
        self.session.commit()
        return article

    def get_article(self, user: User, article_id: int) -> tables.Article:
        return self._get_by_id(article_id)

    def update_article(self, user: User, article_id: int, article_data: ArticleUpdate, status: Optional[ArticleStatus] = None) -> tables.Article:
        article = self._get_by_id(article_id)
        if user.role == UserRole.DEFAULT:
            self.raise_401_with_text("You can't do that")
        if user.role == UserRole.WRITER:
            if article.status == ArticleStatus.DRAFT and article_data.status != ArticleStatus.PUBLICATED:
                self.raise_401_with_text("You can't do that")

        for field, value in article_data:
            setattr(article, field, value)
        self.session.commit()
        return article

    def leave_comment(self, user:User, article_id: int, comment: BaseComment):
        db_comment = tables.Comment()
        db_comment.text = comment.text
        db_comment.user_id = user.id
        db_comment.article_id = article_id
        db_comment.status = CommentStatus.PUBLICATED
        self.session.add(db_comment)
        self.session.commit()
        return db_comment

    def get_comments(self, article_id):
        query = self.session.query(tables.Comment)
        query = query.filter_by(article_id=article_id)
        query = query.filter_by(status=CommentStatus.PUBLICATED)
        comments = query.all()
        return comments

    def delete_article(self, user: User, article_id: int):
        article = self._get_by_id(article_id)
        if article.user_id != user.id and user.role != UserRole.ADMIN:
            self.raise_401_with_text("You can't do that")
        self.session.delete(article)
        self.session.commit()