
import asyncio

from fastapi import FastAPI, APIRouter, Request, Response

from hypercorn.asyncio import serve
from hypercorn.config import Config

from . import settings, k8sController

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
app = FastAPI()

@app.get("/")
async def root(request: Request):
  content = {}
  for index_name in k8sController.index_list():
    idx = k8sController.get_index(index_name=index_name)
    content['index_name'] = {
      namespace: list(idx[namespace])
      for namespace in idx.keys()
    }
  return JSONResponse(content=content)


async def start(shutdown_event: asyncio.Event):

  config = Config()
  config.bind = [f'0.0.0.0:{settings.PORT}']
  config.use_reloader = settings.DEBUG
  config.worker_class = 'uvloop'
  return await serve(app, config, shutdown_trigger=shutdown_event.wait)