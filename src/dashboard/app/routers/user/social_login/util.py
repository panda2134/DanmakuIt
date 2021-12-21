from fastapi.responses import RedirectResponse
from fastapi import HTTPException, status

from app.config import app_config
from app.db import get_db
from app.models.user import User


class TokenResponse(RedirectResponse):
    def __init__(self, token: str):
        super().__init__(app_config.social_login.jwt_redirect_path+'?token='+token)

async def create_or_update_user(user_model: User) -> None:
    if not await get_db()['user'].count_documents(dict(uid=user_model.uid), limit=1)\
        and not app_config.social_login.allow_registration:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Registration is disabled.')

    await get_db()['user'].update_one(
        dict(connect_uid=user_model.uid),
        {'$set': user_model.dict()},
        upsert=True
    )