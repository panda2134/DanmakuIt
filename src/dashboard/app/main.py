import pathlib
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.routers import router
from app.config import app_config

readme_file = pathlib.Path(__file__).parent.parent / 'README.md'

with readme_file.open('r') as f:
    description = f.read()

app = FastAPI(
    title='DanmakuItPanel',
    description=description
)

app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=app_config.session_secret)
if app_config.debug:
    print('Running in debug mode!')
    app.mount('/static', StaticFiles(directory='static'), name='callback_test')
    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
                       allow_methods=['*'], allow_headers=['*'])


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
