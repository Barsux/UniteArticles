from typing import List, Optional
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from app.models.articles import Article, ArticleStatus, ArticleCreate, ArticleUpdate
from app.services.articles import ArticlesService

router = APIRouter(
    prefix="/articles"
)

@router.get("/", response_model=List[Article])
def get_articles(
        status: Optional[ArticleStatus] = None,
        service: ArticlesService = Depends(),
):
    return service.get_list(status=status)

@router.post("/", response_model=Article)
def create_article(
        article_data: ArticleCreate,
        service: ArticlesService = Depends(),
):
    return service.create_article(article_data)

@router.get("/{article_id}", response_model=Article)
def get_article(
    article_id: int,
    service: ArticlesService = Depends(),
):
    return service.get_article(article_id)

@router.put("/{article_id}", response_model=Article)
def update_article(
        article_id: int,
        article_data: ArticleUpdate,
        status: Optional[ArticleStatus] = None,
        service: ArticlesService = Depends(),
):
    return service.update_article(article_id, article_data)


@router.delete("/{article_id}")
def delete_article(
        article_id: int,
        service: ArticlesService = Depends(),
):
    service.delete_article(article_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)