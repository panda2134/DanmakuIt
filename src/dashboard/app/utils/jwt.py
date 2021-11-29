from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from app.config import app_config
from app.models.user import User
from app.db import db


def create_jwt(user: User):
    expire_at = datetime.utcnow() + app_config.social_login.jwt_token_age
    return jwt.encode({'sub': user.uid, 'exp': expire_at},
                      app_config.social_login.jwt_secret,
                      algorithm=app_config.social_login.jwt_algorithm)


bearer_scheme = HTTPBearer()


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> User:
    try:
        payload = jwt.decode(token.credentials, app_config.social_login.jwt_secret,
                             algorithms=[app_config.social_login.jwt_algorithm])
        user = await db['user'].find_one({'connect_uid': payload['sub']})
        if user is None: raise ValueError('User not found')
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid JWT token.',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return User.parse_obj(user)
