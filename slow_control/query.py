from ariadne import QueryType
from .models import Runfile, Device
from channels.db import database_sync_to_async

from .common import  DATABASE, str_to_list

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""

@database_sync_to_async
def _get_run( id ):
    return Runfile.objects.using( DATABASE ).get(pk = id)

@database_sync_to_async
def _filter_runs( names, minStartDate, maxStartDate, minSubDate, maxSubDate, status):
    # if (all([arg is None for arg in (names, minStartDate, maxStartDate, status)]):
    #     raise ValueError("At least one field filter must be specified")   
    queryset = Runfile.objects.using( DATABASE ).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if status:
        queryset = queryset.filter(status__exact=status)
    if minStartDate:
        queryset = queryset.filter(startTime__gte=minStartDate)
    if maxStartDate:
        queryset = queryset.filter(startTime__lte=maxStartDate)
    if minSubDate:
        queryset = queryset.filter(submitted__gte=minSubDate)
    if maxSubDate:
        queryset = queryset.filter(submitted__lte=maxSubDate)
    return list( queryset )

@database_sync_to_async
def _get_device( name ):
    return Device.objects.using( DATABASE ).get( name = name )

@database_sync_to_async
def _filter_devices( names, isOnline ):
    # if (all([arg is None for arg in (names, isOnline)]):
    #     raise ValueError("At least one field filter must be specified")   
    queryset = Device.objects.using( DATABASE ).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if isOnline is not None:
        queryset = queryset.filter(isOnline__exact=isOnline)

    return list( queryset )


"""
Queries
"""

query = QueryType()

@query.field("getRun")
async def resolve_run(*_, id):
    return await _get_run( id )

@query.field("getRuns")
async def resolve_runs(*_, names=None, minStartDate=None, maxStartDate=None, 
                        minSubDate=None, maxSubDate=None, status=None):
    return await _filter_runs(names, minStartDate, maxStartDate,
                             minSubDate, maxSubDate, status)


@query.field("getDevice")
async def resolve_device(*_, name):
    device  = await _get_device( name )
    device.states = str_to_list(device.states)
    return device

@query.field("getDevices")
async def resolve_devices(*_, names=None, isOnline=None):
    devices = await _filter_devices(names, isOnline)
    for i, dev in enumerate(devices):
        devices[i].states = str_to_list( dev.states )
    return devices
