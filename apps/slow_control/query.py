from ariadne import QueryType
from .models import RunConfig, RunConfigStep, Device
from channels.db import database_sync_to_async

from .common import DATABASE, MAX_RUN_CONFIGS

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""


@database_sync_to_async
def _get_run_config(id):
    run_config = RunConfig.objects.using(DATABASE).get(pk=id)
    run_config.steps = list(run_config.runconfigstep_set.all())
    return run_config


@database_sync_to_async
def _get_step(id):
    return RunConfigStep.objects.using(DATABASE).get(pk=id)


@database_sync_to_async
def _filter_runs(names=None, minLoadDate=None, maxLoadDate=None):
    queryset = RunConfig.objects.using(DATABASE).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if minLoadDate:
        queryset = queryset.filter(lastLoaded__gte=minLoadDate)
    if maxLoadDate:
        queryset = queryset.filter(lastLoaded__lte=maxLoadDate)
    for run_config in queryset:
        run_config.steps = list(run_config.runconfigstep_set.all())
    return list(queryset)


@database_sync_to_async
def _get_device(name):
    try:
        return Device.objects.using(DATABASE).get(name=name)
    except Exception as e:
        raise Exception(f'Error for device name "{name}"\n{e}')


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
async def resolve_run_config_step(*_, stepID, runConfigId=None):
    '''Fetch RunConfig, then search the steps for stepID. Return None if step not found'''
    return await _get_step(stepID)


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
