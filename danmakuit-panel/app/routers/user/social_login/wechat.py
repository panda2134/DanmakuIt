from typing import Optional, List, Dict
from urllib.parse import quote_from_bytes

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ValidationError
from app.db import db
import httpx
from app.config import app_config
from app.models.user import User
from app.routers.user.social_login.response import TokenResponse
from app.utils.jwt import create_jwt

router = APIRouter()


class WeChatAccessTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str
    openid: str


class WeChatUserInfoResponse(BaseModel):
    openid: str
    nickname: str
    sex: int
    province: str
    city: str
    country: str
    headimageurl: Optional[str]
    privilege: List[str]
    unionid: str


async def get_from_wechat_api(client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> Dict:
    try:
        res = await client.get(url, params=params)
        res.raise_for_status()
        return res.json()
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail='WeChat server seems down.')


@router.get('/wechat', status_code=307, response_description='redirect to frontend')
async def connect_to_wechat(code: str):
    # check with wechat server
    async with httpx.AsyncClient() as client:

        # retrieve access token
        res = await get_from_wechat_api(client, 'https://api.weixin.qq.com/sns/oauth2/access_token',
                                        params={
                                            'appid': app_config.social_login.wechat.appid,
                                            'secret': app_config.social_login.wechat.secret,
                                            'code': code,
                                            'grant_type': 'authorization_code'
                                        })

        try:
            res = WeChatAccessTokenResponse(**res)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid authorization code.')

        # download user details
        res = await get_from_wechat_api(client, 'https://api.weixin.qq.com/sns/userinfo',
                                        params={
                                            'access_token': res.access_token,
                                            'openid': res.openid,
                                            'lang': 'zh_CN'
                                        })
        try:
            user_info = WeChatUserInfoResponse(**res)
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail='Failed to grab WeChat user info.')

        try:
            if not user_info.headimageurl:
                raise ValueError('No avatar')
            res = await client.get(user_info.headimageurl)
            res.raise_for_status()
            avatar = f"data:{res.headers['Content-Type']},{quote_from_bytes(await res.content)}"
        except (ValueError, httpx.HTTPError):
            avatar = None

    # if the user exists, update & return a JWT token; else, create a user first.
    user_model = User(uid=f'wechat:{user_info.unionid}',
                      username=user_info.nickname,
                      avatar=avatar)
    await db['user'].update_one(
        dict(connect_uid=user_model.uid),
        {'$set': user_model.dict()},
        upsert=True
    )
    return TokenResponse(create_jwt(user_model))
