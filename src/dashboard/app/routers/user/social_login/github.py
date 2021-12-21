import httpx
from authlib.integrations.starlette_client import StarletteRemoteApp
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
from starlette.requests import Request

from app.db import get_db
from .oauth import oauth
from app.config import app_config
from app.models.user import User
from app.routers.user.social_login.util import TokenResponse, create_or_update_user
from app.utils.jwt import create_jwt

router = APIRouter()

class GitHubUser(BaseModel):
    id: int
    login: str
    avatar_url: HttpUrl

@router.get('/github/login')
async def login_github(request: Request):
    github: StarletteRemoteApp = oauth.create_client('github')
    redirect_uri = app_config.social_login.oauth_redirect_baseurl + request.app.url_path_for('auth_github')
    return await github.authorize_redirect(request, redirect_uri)


@router.get('/github/auth', status_code=307, response_description='redirect to frontend')
async def auth_github(request: Request):
    github: StarletteRemoteApp = oauth.create_client('github')
    token = await github.authorize_access_token(request)
    try:
        res: httpx.Response = await github.get('user', token=token)
        res.raise_for_status()
        user = GitHubUser.parse_obj(res.json())
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='GitHub server seems down.')
    user_model = User(uid=f'github:{user.id}',
                      username=user.login,
                      avatar=user.avatar_url)
    await create_or_update_user(user_model)
    return TokenResponse(create_jwt(user_model))

