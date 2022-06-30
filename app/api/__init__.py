from fastapi import APIRouter

from .articles import router as articles_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(articles_router)