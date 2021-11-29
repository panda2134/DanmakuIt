from fastapi.params import Depends
import httpx
from authlib.integrations.starlette_client import StarletteRemoteApp
from fastapi import APIRouter, HTTPException, status
from motor.metaprogramming import Async
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from starlette.requests import Request

from app.db import get_db
from .oauth import oauth
from app.config import app_config
from app.models.user import User
from app.routers.user.social_login.response import TokenResponse
from app.utils.jwt import create_jwt

router = APIRouter()


class GitLabV4User(BaseModel):
    id: int
    name: str
    username: str
    avatar_url: str


@router.get('/gitlab/login')
async def login_gitlab(request: Request):
    gitlab: StarletteRemoteApp = oauth.create_client('gitlab')
    redirect_uri = app_config.social_login.oauth_redirect_baseurl + request.app.url_path_for('auth_gitlab')
    return await gitlab.authorize_redirect(request, redirect_uri)


@router.get('/gitlab3rd/login')
async def login_gitlab_3rd_party(request: Request):
    gitlab: StarletteRemoteApp = oauth.create_client('gitlab3rd')
    redirect_uri = app_config.social_login.oauth_redirect_baseurl + request.app.url_path_for('auth_gitlab_3rd_party')
    return await gitlab.authorize_redirect(request, redirect_uri)


async def get_user_from_gitlab_api(request: Request, db: AsyncIOMotorDatabase, client_name: str = 'gitlab') -> User:
    gitlab: StarletteRemoteApp = oauth.create_client(client_name)
    token = await gitlab.authorize_access_token(request)
    try:
        res: httpx.Response = await gitlab.get('user', token=token)
        res.raise_for_status()
        user = GitLabV4User.parse_obj(res.json())
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='GitLab server seems down.')
    user_model = User(uid=f'{client_name}:{user.id}',
                      username=user.username,
                      avatar=user.avatar_url)
    await db['user'].update_one(
        dict(connect_uid=user_model.uid),
        {'$set': user_model.dict()},
        upsert=True
    )
    return user_model


@router.get('/gitlab/auth', status_code=307, response_description='redirect to frontend')
async def auth_gitlab(request: Request, db = Depends(get_db)):
    user_model = await get_user_from_gitlab_api(request, db, 'gitlab')
    return TokenResponse(create_jwt(user_model))


@router.get('/gitlab3rd/auth', status_code=307, response_description='redirect to frontend')
async def auth_gitlab_3rd_party(request: Request, db = Depends(get_db)):
    user_model = await get_user_from_gitlab_api(request, db, 'gitlab3rd')
    return TokenResponse(create_jwt(user_model))

