from fastapi import APIRouter

from app.routers.user import router as user_router
from app.routers.room import router as room_router

router = APIRouter()
router.include_router(user_router, prefix='/user')
router.include_router(room_router, prefix='/room')