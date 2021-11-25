from fastapi.responses import RedirectResponse

from app.config import app_config


class TokenResponse(RedirectResponse):
    def __init__(self, token: str):
        super().__init__(app_config.social_login.jwt_redirect_path+'?token='+token)