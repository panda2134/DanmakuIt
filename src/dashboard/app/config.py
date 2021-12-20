import datetime
from logging import log
from typing import Any
from os import environ

from pydantic import BaseSettings, Field, AnyUrl, HttpUrl

web_origin = environ.get('WEB_ORIGIN', 'http://127.0.0.1')
class SocialLoginSettings(BaseSettings):
    class WeChatLoginSettings(BaseSettings):
        appid: str = Field('wechat-appid')
        secret: str = Field('wechat-secret')

    class GitLabLoginSettings(BaseSettings):
        base_url: str = 'https://gitlab.com'
        appid: str = Field('gitlab-appid')
        secret: str = Field('gitlab-secret')

    class GitHubLoginSettings(BaseSettings):
        appid: str = Field('github-appid')
        secret: str = Field('github-secret')

    wechat = WeChatLoginSettings() # disabled for now
    github = GitHubLoginSettings(appid=environ.get('GITHUB_APPID', ''),
                                 secret=environ.get('GITHUB_SECRET', ''))
    gitlab = GitLabLoginSettings(appid=environ.get('GITLAB_APPID', ''),
                                 secret=environ.get('GITLAB_SECRET', ''))
    gitlab3rd = GitLabLoginSettings(base_url=environ.get('GITLAB_3RD_BASEURL', ''),
                                    appid=environ.get('GITLAB_3RD_APPID', ''),
                                    secret=environ.get('GITLAB_3RD_SECRET', ''))

    oauth_redirect_baseurl: AnyUrl = Field(f'{web_origin}/api/v1', env='OAUTH_REDIRECT_BASE_URL')
    jwt_secret: str = Field(..., env='JWT_SECRET')
    jwt_algorithm: str = Field('HS256')
    jwt_token_age: datetime.timedelta = Field(datetime.timedelta(days=14))
    jwt_redirect_path: str = '/oauth-token'  # jwt will be appended as query string


class RoomSettings(BaseSettings):
    room_passcode_length: int = Field(6, ge=6, le=16, env='ROOM_PASSCODE_LEN')
    wechat_token_length: int = Field(12, ge=8, le=16, env='WECHAT_TOKEN_LEN')
    wechat_retry_secs: int = Field(60, env='WECHAT_RETRY_SECS')

mongo_user = environ.get('MONGO_INITDB_ROOT_USERNAME')
mongo_pass = environ.get('MONGO_INITDB_ROOT_PASSWORD')

class Settings(BaseSettings):
    debug: bool = Field(False, env='DEBUG')
    origin: str = Field('http://127.0.0.1', env='WEB_ORIGIN')
    social_login = SocialLoginSettings()
    mongo_uri: AnyUrl = Field(f'mongodb://{mongo_user}:{mongo_pass}@mongo:27017')
    controller_url: AnyUrl = Field('http://controller:8000')
    mongo_db_name: str = Field('danmakuit', env='MONGO_DB_NAME')
    room = RoomSettings()
    pulsar_enabled = True
    session_secret: str = Field(..., env='SESSION_SECRET')
    max_rollback_retry = 10
    wechat_token_salt: bytes = Field(..., env='WECHAT_TOKEN_SALT')


app_config = Settings()