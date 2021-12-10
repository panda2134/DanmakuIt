import pathlib
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware


from app.routers import router
from app.http_client import http_client
from app.config import app_config

parent_dir = pathlib.Path(__file__).parent
readme_file = parent_dir / 'README.md'
static_dir = parent_dir / 'static'

with readme_file.open('r') as f:
    description = f.read()

app = FastAPI(
    title='DanmakuIt Dashboard API',
    description=description,
    root_path="/api/v1",
    servers=[
        {"url": "https://danmakuit.panda2134.site/api/v1", "description": "Development server"},
    ],
)


@app.on_event('shutdown')
async def on_shutdown():
    await http_client.aclose()

app.include_router(router)
app.add_middleware(SessionMiddleware, secret_key=app_config.session_secret)
if app_config.debug:
    print('Running in debug mode!')
    app.mount('/static', StaticFiles(directory=static_dir), name='callback_test')
    app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
                       allow_methods=['*'], allow_headers=['*'])

uvicorn.run(app, host="0.0.0.0", port=8000)
