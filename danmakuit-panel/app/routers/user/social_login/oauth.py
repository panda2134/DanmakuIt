from authlib.integrations.starlette_client import OAuth
from app.config import app_config, SocialLoginSettings

oauth = OAuth()


def register_gitlab(client_name: str, settings: SocialLoginSettings.GitLabLoginSettings):
    oauth.register(client_name,
                   client_id=settings.appid,
                   client_secret=settings.secret,
                   authorize_url=settings.base_url + '/oauth/authorize',
                   access_token_url=settings.base_url + '/oauth/token',
                   api_base_url=settings.base_url + '/api/v4/',
                   client_kwargs={'scope': 'read_user'})


register_gitlab('gitlab', app_config.social_login.gitlab)
register_gitlab('gitlab3rd', app_config.social_login.gitlab3rd)
oauth.register('github',
               client_id=app_config.social_login.github.appid,
               client_secret=app_config.social_login.github.secret,
               access_token_url='https://github.com/login/oauth/access_token',
               authorize_url='https://github.com/login/oauth/authorize',
               api_base_url='https://api.github.com/',
               client_kwargs={'scope': 'read:user'})