import httpx
from authlib.integrations.starlette_client import StarletteRemoteApp
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, HttpUrl
from starlette.requests import Request
from .oauth import oauth
from app.db import db
from app.models.user import User
from app.routers.user.social_login.response import TokenResponse
from app.utils.jwt import create_jwt

router = APIRouter()

class GitHubUser(BaseModel):
    id: int
    login: str
    avatar_url: HttpUrl

@router.get('/github/login')
async def login_github(request: Request):
    github: StarletteRemoteApp = oauth.create_client('github')
    redirect_uri = request.url_for('auth_github')
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
    await db['user'].update_one(
        dict(connect_uid=user_model.uid),
        {'$set': user_model.dict()},
        upsert=True
    )
    return TokenResponse(create_jwt(user_model))