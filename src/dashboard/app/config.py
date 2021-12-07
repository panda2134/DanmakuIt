import datetime
from typing import Any

from pydantic import BaseSettings, Field, AnyUrl, HttpUrl



class SocialLoginSettings(BaseSettings):
    class WeChatLoginSettings(BaseSettings):
        appid: str = Field('wechat-appid', env='WECHAT_APPID')
        secret: str = Field('wechat-secret', env='WECHAT_SECRET')

    class GitLabLoginSettings(BaseSettings):
        base_url: str = 'https://gitlab.com'
        appid: str = Field('gitlab-appid')
        secret: str = Field('gitlab-secret')

    class GitHubLoginSettings(BaseSettings):
        appid: str = Field('github-appid')
        secret: str = Field('github-secret')

    wechat = WeChatLoginSettings()
    github = GitHubLoginSettings(appid='***REMOVED***',
                                 secret='***REMOVED***')
    gitlab = GitLabLoginSettings(appid='***REMOVED***',
                                 secret='***REMOVED***')
    gitlab3rd = GitLabLoginSettings(base_url='https://git.tsinghua.edu.cn',
                                    appid='***REMOVED***',
                                    secret='***REMOVED***')

    oauth_redirect_baseurl: AnyUrl = Field('https://danmakuit.panda2134.site/api/v1', env='OAUTH_REDIRECT_BASE_URL')
    jwt_secret: str = Field('***REMOVED***', env='JWT_SECRET')
    jwt_algorithm: str = Field('HS256')
    jwt_token_age: datetime.timedelta = Field(datetime.timedelta(days=14))
    jwt_redirect_path: str = '/oauth-token' # jwt will be appended as query string


class RoomSettings(BaseSettings):
    danmaku_wall_prefix: HttpUrl = Field('http://127.0.0.1:3000/wall/')
    room_passcode_length: int = Field(6, ge=6, le=16)
    wechat_token_length: int = Field(12, ge=8, le=16, env='WECHAT_TOKEN_LEN')
    wechat_retry_secs: int = Field(60, env='WECHAT_RETRY_SECS')

class Settings(BaseSettings):
    debug: bool = Field(False, env='DEBUG')
    social_login = SocialLoginSettings()
    mongo_uri: AnyUrl = Field('mongodb://root:password@mongo:27017')
    controller_url: AnyUrl = Field('http://controller:8000')
    mongo_db_name: str = 'danmakuit'
    room = RoomSettings()
    pulsar_enabled = True
    session_secret = Field('***REMOVED***', env='SESSION_SECRET')
    max_rollback_retry = 10
    wechat_token_salt: bytes = Field(..., env='WECHAT_TOKEN_SALT')

app_config = Settings()
