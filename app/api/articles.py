from typing import List, Optional
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from app.models.articles import Article, ArticleStatus, ArticleCreate, ArticleUpdate, BaseMark, Mark, InputArticle
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
        article_data: InputArticle,
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
        article_data: InputArticle,
        user: User = Depends(get_curr_user),
        service: ArticlesService = Depends(),
):
    return service.update_article(user, article_id, article_data)

@router.put("/{article_id}/change_status",response_model=Article)
def change_status(
        status: ArticleStatus,
        article_id: int,
        user: User = Depends(get_curr_user),
        service: ArticlesService =  Depends()
):
    return service.change_status(article_id, user, status)
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

    x = service.leave_comment(user, article_id, comment)
    print(x)
    return x

@router.delete("/{article_id}")
def delete_article(
        article_id: int,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user),
):
    service.delete_article(user, article_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{article_id}/mark", response_model=Article)
def leave_mark(
        mark: BaseMark,
        article_id: int,
        service: ArticlesService = Depends(),
        user: User = Depends(get_curr_user),
):
    return service.leave_mark(user, article_id, mark)