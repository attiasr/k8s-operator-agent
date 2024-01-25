
import asyncio

from fastapi import FastAPI, Request

from hypercorn.asyncio import serve
from hypercorn.config import Config
from langserve import add_routes

from . import agent
from . import settings, k8sController

from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
async def root(request: Request):
  content = {'crds': k8sController.get_crds() }

  for index_name in k8sController.index_list():
    idx = k8sController.get_index(index_name=index_name)
    content[index_name] = list(idx.keys())

  return JSONResponse(content=content)


add_routes(
  app,
  agent.chain,
  path='/agent'
)

async def start(shutdown_event: asyncio.Event):
  config = Config()
  config.bind = [f'0.0.0.0:{settings.PORT}']
  config.use_reloader = settings.DEBUG
  config.worker_class = 'uvloop'
  return await serve(app, config, shutdown_trigger=shutdown_event.wait)