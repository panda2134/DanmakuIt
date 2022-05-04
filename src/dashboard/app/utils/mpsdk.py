import os

from weixin import WXAPPAPI

appid, app_secret = os.getenv('WECHAT_MP_APPID'), os.getenv('WECHAT_MP_APPSECRET')
mpsdk = WXAPPAPI(appid=appid, app_secret=app_secret, grant_type='client_credential')