from fastapi import APIRouter

from .articles import router as articles_router


router = APIRouter()
router.include_router(articles_router)