from typing import Iterable, Mapping
import asyncio
import kopf
from . import settings

INDEX_MAP: Mapping[str, kopf.Index] = {}


def _update_index_map(**kwargs):
  global INDEX_MAP
  for key, value in kwargs.items():
    if isinstance(value, kopf.Index):
      INDEX_MAP[key] = value

def index_list() -> Iterable[str]:
  return list(INDEX_MAP.keys())

def get_index(index_name: str) -> kopf.Index:
  return INDEX_MAP.get(index_name)

@kopf.on.startup()
async def configure(settings: kopf.OperatorSettings, logger, **_):
  logger.info("configuring k8sController")
  settings.persistence.diffbase_storage = kopf.StatusDiffBaseStorage(field='status.diff-base')

@kopf.index('apps', 'v1', 'deployment')
async def deployments_idx(name, namespace, logger, **kwargs):
  logger.info('index deployments')
  _update_index_map(**kwargs)
  return {namespace: name}
  # result in: (see https://kopf.readthedocs.io/en/stable/indexing/#index-content)
  # {'namespace1': ['nameA', 'nameB'],
  #  'namespace2': ['nameC']}

@kopf.index('', 'v1', 'pod')
async def pods_idx(name, namespace, logger, **kwargs):
  logger.info('index pods')
  _update_index_map(**kwargs)
  return {namespace: name}


async def start(shutdown_event: asyncio.Event):
  kopf.configure(verbose=settings.DEBUG)
  return await kopf.operator(clusterwide=True,
                             stop_flag=shutdown_event)