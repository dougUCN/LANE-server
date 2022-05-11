from ariadne import QueryType
from .models import Runfile, Device
from channels.db import database_sync_to_async

from .common import  DATABASE

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""

@database_sync_to_async
def _get_run( name ):
    return Runfile.objects.using( DATABASE ).get(name)

@database_sync_to_async
def _filter_runs( names, minStartDate, maxStartDate, status):
    # if (all([arg is None for arg in (names, minStartDate, maxStartDate, status)]):
    #     raise ValueError("At least one field filter must be specified")   
    queryset = Runfile.objects.using( DATABASE ).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if status:
        queryset = queryset.filter(status__in=status)
    if minStartDate:
        queryset = queryset.filter(start_time__gte=minStartDate)
    if maxStartDate:
        queryset = queryset.filter(start_time__lte=maxStartDate)

    return list( queryset )

@database_sync_to_async
def _get_device( name ):
    return Device.objects.using( DATABASE ).get(name)

@database_sync_to_async
def _filter_devices( names, isOnline ):
    # if (all([arg is None for arg in (names, isOnline)]):
    #     raise ValueError("At least one field filter must be specified")   
    queryset = Runfile.objects.using( DATABASE ).all()
    if names:
        queryset = queryset.filter(name__in=names)
    if isOnline is not None:
        queryset = queryset.filter(is_online__exact=isOnline)

    return list( queryset )


"""
Queries
"""

query = QueryType()

@query.field("getRun")
async def resolve_run(*_, name):
    return await _get_run( name=name )

@query.field("getRuns")
async def resolve_runs(*_, names=None, minStartDate=None,
                                maxStartDate=None, status=None):
    return await _filter_runs(names, minStartDate, maxStartDate, status)


@query.field("getDevice")
async def resolve_run(*_, name):
    return await _get_device( name=name )

@query.field("getDevices")
async def resolve_devices(*_, names=None, isOnline=None):
    return await _filter_devices(names, isOnline)
