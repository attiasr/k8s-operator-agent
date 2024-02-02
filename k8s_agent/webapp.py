
import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from hypercorn.asyncio import serve
from hypercorn.config import Config
from langserve import add_routes

from . import agent, settings

from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
async def root():
  print(type(asyncio.get_event_loop_policy().get_event_loop()))
  return RedirectResponse('/docs')


add_routes(
  app,
  agent.executor,
  path='/k8s-agent'
)


async def start(shutdown_event: asyncio.Event):
  config = Config()
  config.bind = [f'0.0.0.0:{settings.PORT}']
  config.use_reloader = settings.DEBUG
  return await serve(app, config, shutdown_trigger=shutdown_event.wait)