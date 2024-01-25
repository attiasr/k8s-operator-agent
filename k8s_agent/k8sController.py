from typing import Iterable, Mapping
import asyncio
import kopf
import pykube
from . import settings

INDEX_MAP: Mapping[str, kopf.Index] = {}
CRDS: Iterable[pykube.CustomResourceDefinition]

def _update_index_map(**kwargs):
  global INDEX_MAP
  for key, value in kwargs.items():
    if isinstance(value, kopf.Index):
      INDEX_MAP[key] = value

def index_list() -> Iterable[str]:
  return list(INDEX_MAP.keys())

def get_index(index_name: str) -> kopf.Index:
  return INDEX_MAP.get(index_name)

def get_crds():
  return CRDS

@kopf.on.startup()
async def configure(settings: kopf.OperatorSettings, logger, **_):
  logger.info("configuring k8sController")
  global CRDS
  api = pykube.HTTPClient(pykube.KubeConfig.from_env())
  CRDS = [ crd.name for crd in pykube.CustomResourceDefinition.objects(api).all() ]
  settings.persistence.diffbase_storage = kopf.StatusDiffBaseStorage(field='status.diff-base')

@kopf.index('apps', 'v1', 'deployment')
async def deployments_idx(name, namespace, body, **kwargs):
  _update_index_map(**kwargs)
  ## NOTE: see https://kopf.readthedocs.io/en/stable/indexing/#index-content
  return {f'{namespace}:{name}': body}

@kopf.index('apps', 'v1', 'statefulset')
async def statefulsets_idx(name, namespace, body, **kwargs):
  _update_index_map(**kwargs)
  return {f'{namespace}:{name}': body}

@kopf.index('apps', 'v1', 'daemonset')
async def daemonsets_idx(name, namespace, body, **kwargs):
  _update_index_map(**kwargs)
  return {f'{namespace}:{name}': body}

@kopf.index('', 'v1', 'pod')
async def pods_idx(name, namespace, body, **kwargs):
  _update_index_map(**kwargs)
  return {f'{namespace}:{name}': body}


async def start(shutdown_event: asyncio.Event):
  kopf.configure(verbose=settings.DEBUG)
  return await kopf.operator(clusterwide=True,
                             stop_flag=shutdown_event)