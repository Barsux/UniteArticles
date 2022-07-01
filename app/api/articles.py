from typing import List, Optional
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from app.models.articles import Article, ArticleStatus, ArticleCreate, ArticleUpdate
from app.models.auth import BaseComment, Comment
from app.services.articles import ArticlesService
from app.services.auth import User, get_curr_user

router = APIRouter(
    prefix="/articles"
)

@router.get("/", response_model=List[Article])
def get_articles(
        only_mine: bool = False,
        status: Optional[ArticleStatus] = None,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user)
):
    return service.get_list(user, only_mine=only_mine, status=status)

@router.post("/", response_model=Article)
def create_article(
        article_data: ArticleCreate,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user),
):
    return service.create_article(user, article_data)

@router.get("/{article_id}", response_model=Article)
def get_article(
        article_id: int,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user)
):
    return service.get_article(user, article_id)

@router.put("/{article_id}", response_model=Article)
def update_article(
        article_id: int,
        article_data: ArticleUpdate,
        status: Optional[ArticleStatus] = None,
        user: User = Depends(get_curr_user),
        service: ArticlesService = Depends(),
):
    return service.update_article(user, article_id, article_data)
@router.get("/{article_id}/comment", response_model=List[Comment])
def get_comments(
        article_id: int,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user)
):
    return service.get_comments(article_id)
@router.put("/{article_id}/comment", response_model=Comment)
def leave_comment(
        article_id: int,
        comment: BaseComment,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user)
):
    return service.leave_comment(user, article_id, comment)

@router.delete("/{article_id}")
def delete_article(
        article_id: int,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user),
):
    service.delete_article(user, article_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)