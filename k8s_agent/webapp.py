import asyncio

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from hypercorn.asyncio import serve
from hypercorn.config import Config
from langserve import add_routes

from . import agent, settings

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
async def root():
  return RedirectResponse('/docs')


add_routes(
  app,
  agent.executor,
  path='/k8s-agent',
  config_keys=["metadata", "configurable", "tags"],
)


async def start(shutdown_event: asyncio.Event):
  config = Config()
  config.bind = [f'0.0.0.0:{settings.PORT}']
  config.use_reloader = settings.DEBUG
  config.accesslog = '-'
  return await serve(app, config, shutdown_trigger=shutdown_event.wait)