import datetime

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
    github = GitHubLoginSettings(appid='88437af4e0d8b54fd8be',
                                 secret='1d3d9bce615f2d442942ca7d57ab8550cc43d819')
    gitlab = GitLabLoginSettings(appid='4076ef287b978facffa5459a4472339587103eae4e16c1357a7445bec16d0d5f',
                                 secret='10682e99ea72c9ca18618c25391398fa74299fc81654704613150e73ef0ab60c')
    gitlab3rd = GitLabLoginSettings(base_url='https://git.tsinghua.edu.cn',
                                    appid='37313c6a3bb02d54c1fa51888fbae60d81c55ff18919c9180c01be09e7cac92b',
                                    secret='348dddc1f01ba1152f84eece0045f50291ab0d91d6d99677a2226b3c503e7cca')

    jwt_secret: str = Field('3e43a35fe78d3db766e2c4d1fa82658a147a21e41963e111616a8d9a15a1840c', env='JWT_SECRET')
    jwt_algorithm: str = Field('HS256')
    jwt_token_age: datetime.timedelta = Field(datetime.timedelta(days=14))
    jwt_redirect_path: str = '/static/index.html' # jwt will be appended as query string


class RoomSettings(BaseSettings):
    danmaku_wall_prefix: HttpUrl = Field('http://127.0.0.1:3000/wall/')
    room_passcode_length: int = Field(6, ge=6, le=16)
    wechat_token_length: int = Field(12, ge=8, le=16)


class Settings(BaseSettings):
    debug: bool = Field(False, env='DEBUG')
    social_login = SocialLoginSettings()
    mongo_url: AnyUrl = Field('mongodb://localhost:27017')
    controller_url: HttpUrl = Field('http://localhost:9000')
    mongo_db_name: str = 'danmakuit'
    room = RoomSettings()
    session_secret = Field('729b4532d811a1122f61ddc7bfe9711d', env='SESSION_SECRET')
    room_passcode_salt = Field('b03f48507082262537fe82934ee04d4d', env='ROOM_PASSCODE_SECRET')
    wechat_passcode_salt = Field('486b0f76b2a165173a0c83cf82f5dafa', env='WECHAT_PASSCODE_SECRET')


app_config = Settings()
