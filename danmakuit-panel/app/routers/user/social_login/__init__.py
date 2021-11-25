from fastapi import APIRouter
from .github import router as github_router
from .gitlab import router as gitlab_router
from .wechat import router as wechat_router

router = APIRouter()

router.include_router(github_router)
router.include_router(gitlab_router)
router.include_router(wechat_router)