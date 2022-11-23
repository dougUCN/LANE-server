from ariadne import QueryType
from .models import RunConfig, Device
from channels.db import database_sync_to_async

from .common import get_step, DATABASE, MAX_RUN_CONFIGS

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""


@database_sync_to_async
def _get_run_config(id):
    return RunConfig.objects.using(DATABASE).get(pk=id)


@database_sync_to_async
def _filter_runs(names=None, minLoadDate=None, maxLoadDate=None):
    queryset = RunConfig.objects.using(DATABASE).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if minLoadDate:
        queryset = queryset.filter(lastLoaded__gte=minLoadDate)
    if maxLoadDate:
        queryset = queryset.filter(lastLoaded__lte=maxLoadDate)
    return list(queryset)


@database_sync_to_async
def _get_device(name):
    return Device.objects.using(DATABASE).get(name=name)


@database_sync_to_async
def _filter_devices(names, isOnline):
    queryset = Device.objects.using(DATABASE).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if isOnline is not None:
        queryset = queryset.filter(isOnline__exact=isOnline)

    return list(queryset)


"""
Queries
"""

query = QueryType()


@query.field("getRunConfig")
async def resolve_run_config(*_, id):
    return await _get_run_config(id)


@query.field("getRunConfigStep")
async def resolve_run_config_step(*_, runConfigID, stepID):
    '''Fetch RunConfig, then search the steps for stepID. Return None if step not found'''
    runConfig = await _get_run_config(runConfigID)
    _, step = get_step(stepID, runConfig['steps'])
    return step


@query.field("getRunConfigs")
async def resolve_run_configs(*_):
    runConfigs = await _filter_runs()
    canCreateNewRun = len(runConfigs) < MAX_RUN_CONFIGS
    if not runConfigs:
        runConfigs = None
    return {"runConfigs": runConfigs, "canCreateNewRun": canCreateNewRun}


@query.field("getDevice")
async def resolve_device(*_, name):
    return await _get_device(name)


@query.field("getDevices")
async def resolve_devices(*_, names=None, isOnline=None):
    return await _filter_devices(names, isOnline)
