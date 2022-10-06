from typing import List, Optional

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import datetime
from app import tables
from app.database import get_session
from app.base import SQL_Divider
from app.models.articles import ArticleStatus, ArticleSearch, BaseMark, InputArticle, BaseTag
from app.models.auth import User, UserRole, BaseComment, CommentStatus, Comment

NOT_ALLOWED = "You are not allowed to do that."

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

    def _get_by_id(self, article_id: int) -> tables.Article:
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
            if not SQL_Divider.check_intersection(user.role, (UserRole.ADMIN, UserRole.MODERATOR)):
                self.raise_401_with_text(NOT_ALLOWED)
            query = query.filter_by(status=status)
        #if only_mine:
        #    query = query.filter_by(user_id=user.id)
        query=query.order_by(tables.Article.last_used_date.desc())
        articles = query.all()
        print(articles)
        return articles

    def create_article(self, user: User, article_data: InputArticle) -> tables.Article:
        print(user.role)
        if not SQL_Divider.check_intersection(user.role, (UserRole.ADMIN, UserRole.WRITER)):
            self.raise_401_with_text(NOT_ALLOWED)
        article = tables.Article()
        article.header = article_data.header
        article.text = article_data.text
        article.user_ids = SQL_Divider.add_element(article.user_ids, str(user.id))
        article.status = ArticleStatus.DRAFT
        article.creation_date = datetime.now()
        article.last_used_date = datetime.now()
        article.summary_mark = 0
        article.votes = 0
        article.tags = ""
        self.session.add(article)
        self.session.commit()
        return article

    def get_article(self, user: User, article_id: int) -> tables.Article:
        return self._get_by_id(article_id)

    def update_article(self, user: User, article_id: int, article_data: InputArticle) -> tables.Article:
        article = self._get_by_id(article_id)
        if SQL_Divider.check_is_inside(user.role, UserRole.DEFAULT):
            self.raise_401_with_text(NOT_ALLOWED)
        elif SQL_Divider.check_is_inside(user.role, UserRole.WRITER):
            if article.status == ArticleStatus.DRAFT and not (User.id == article.user_id) and not SQL_Divider.check_is_inside(user.role, UserRole.ADMIN):
                self.raise_401_with_text(NOT_ALLOWED)
        if article.status == ArticleStatus.APPROWED:
            self.raise_401_with_text(NOT_ALLOWED)
        article.header = article_data.header
        article.text = article_data.text
        article.last_used_date = datetime.now()
        article.user_ids = SQL_Divider.add_element(article.user_ids, str(user.id))
        self.session.commit()
        return article

    def change_status(self, article_id: int, user: User, status: ArticleStatus) -> tables.Article:
        db_article = self._get_by_id(article_id)
        if SQL_Divider.check_intersection(user.role, (UserRole.DEFAULT, UserRole.BANNED)):
            self.raise_401_with_text(NOT_ALLOWED)
        elif SQL_Divider.check_is_inside(user.role, UserRole.WRITER):
            if db_article.status == ArticleStatus.DRAFT and status != ArticleStatus.PUBLICATED:
                self.raise_401_with_text(NOT_ALLOWED)
        elif SQL_Divider.check_is_inside(user.role, UserRole.MODERATOR):
            if status == ArticleStatus.DRAFT or db_article.status == ArticleStatus.DRAFT:
                self.raise_401_with_text(NOT_ALLOWED)
        db_article.status = status
        self.session.commit()
        return db_article

    def leave_comment(self, user:User, article_id: int, comment: BaseComment) -> tables.Comment:
        db_article = self._get_by_id(article_id)
        if SQL_Divider.check_is_inside(user.role, UserRole.BANNED):
            self.raise_401_with_text(NOT_ALLOWED)
        if db_article.status == ArticleStatus.DRAFT:
            self.raise_401_with_text(NOT_ALLOWED)
        db_comment = tables.Comment(**comment.dict())
        db_comment.user_id = user.id
        db_comment.article_id = article_id
        db_comment.status = CommentStatus.PUBLICATED
        self.session.add(db_comment)
        self.session.commit()
        comm = Comment.from_orm(db_comment)
        return comm

    def get_comments(self, article_id) -> List[tables.Comment]:
        query = self.session.query(tables.Comment)
        query = query.filter_by(article_id=article_id)
        query = query.filter_by(status=CommentStatus.PUBLICATED)
        comments = query.all()
        return comments

    def delete_article(self, user: User, article_id: int):
        article = self._get_by_id(article_id)
        if article.user_id != user.id and SQL_Divider.check_is_inside(user.role, UserRole.ADMIN):
            self.raise_401_with_text(NOT_ALLOWED)
        elif article.user_id == user.id and article.status != ArticleStatus.DRAFT:
            self.raise_401_with_text(NOT_ALLOWED)
        self.session.delete(article)
        self.session.commit()

    def leave_mark(self, user: User, article_id: int, mark: BaseMark) -> tables.Article:
        db_article = self._get_by_id(article_id)
        if db_article.status == ArticleStatus.DRAFT:
            self.raise_401_with_text(NOT_ALLOWED)
        if SQL_Divider.check_is_inside(user.role, UserRole.BANNED):
            self.raise_401_with_text(NOT_ALLOWED)
        operation = (
            self.session
                .query(tables.Mark)
                .filter_by(id=article_id)
                .filter_by(user_id=user.id)
                .first()
        )
        if operation:
            self.raise_400_with_text("You already marked that article")
        db_mark = tables.Mark(**mark.dict())
        db_mark.article_id = article_id
        db_mark.user_id = user.id
        db_article.summary_mark += db_mark.mark
        db_article.votes += 1
        self.session.add(db_mark)
        self.session.commit()
        return db_article

    def add_tag(self, tag: BaseTag):
        db_tag = tables.Tag(**tag.dict())
        self.session.add(db_tag)
        self.session.commit()
        return db_tag

    def get_tags(self, user) -> List[tables.Tag]:
        query = self.session.query(tables.Article)
        tags = query.all()
        return tags

    def add_tag_to_article(self, user: User, tag: str, article_id: int):
        db_tag = self.session.query(tables.Tag).filter_by(tag=tag).first()
        if not db_tag:
            self.raise_400_with_text("Tag not found")
        db_article = self._get_by_id(article_id)
        if db_article.status == ArticleStatus.DRAFT:
            self.raise_401_with_text(NOT_ALLOWED)
        if SQL_Divider.check_is_inside(user.role, UserRole.BANNED):
            self.raise_401_with_text(NOT_ALLOWED)
        if(SQL_Divider.check_is_inside(db_article.tags, tag)):
            self.raise_400_with_text("Tag already added")
        db_article.tags = SQL_Divider.add_element(db_article.tags, str(db_tag.id))
        self.session.commit()
        return db_article

    def search_articles(self, user, search: ArticleSearch):
        query = self.session.query(tables.Article)
        if search.title != "string":
            query = query.filter(tables.Article.header.like(f"%{search.title}%"))
        if search.text != "string":
            query = query.filter(tables.Article.text.like(f"%{search.text}%"))
        if search.authors != "string":
            query = query.filter(tables.Article.user_id.like(f"%{search.authors}%"))
        if search.tags != "string":
            query = query.filter(tables.Article.tags.like(f"%{search.tags}%"))
        if search.mark != "string":
            if(search.mark[0] not in ('>', '<')):
                query = query.filter(tables.Article.summary_mark == search.mark)
            elif(search.mark[0] == '>'):
                query = query.filter(tables.Article.summary_mark > search.mark[1:])
            else:
                query = query.filter(tables.Article.summary_mark < search.mark[1:])
        articles = query.all()
        return articles