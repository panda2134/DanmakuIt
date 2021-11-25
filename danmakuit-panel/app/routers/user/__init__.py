from fastapi import APIRouter, Depends

from app.models.user import User
from app.routers.user.social_login import router as social_login_router
from app.utils.jwt import get_current_user

router = APIRouter(tags=['user'])

router.include_router(social_login_router, prefix='/social-login')


@router.get('/me', response_model=User)
async def user_information(user: User = Depends(get_current_user)):
    return user
