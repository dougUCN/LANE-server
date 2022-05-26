from ariadne import QueryType
from .models import Histogram
from channels.db import database_sync_to_async

from .common import chooseDatabase

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""


@database_sync_to_async
def _list_histograms(database_name):
    return list(Histogram.objects.using(database_name).all().values_list('id', flat=True))


@database_sync_to_async
def _get_histogram(id, database_name):
    return Histogram.objects.using(database_name).get(id=id)


@database_sync_to_async
def _filter_histograms(ids, names, types, minDate, maxDate, isLive):
    queryset = Histogram.objects.using(chooseDatabase(isLive)).all()
    if ids:
        queryset = queryset.filter(id__in=ids)
    if names:
        queryset = queryset.filter(name__in=names)
    if types:
        queryset = queryset.filter(type__in=types)
    if minDate:
        queryset = queryset.filter(created__gte=minDate)
    if maxDate:
        queryset = queryset.filter(created__lte=maxDate)

    return list(queryset)


"""
Queries
"""

query = QueryType()


@query.field("listHistograms")
async def list_histograms(*_, isLive=False):
    '''
    Lists the IDs of all histograms in the database

    If isLive, pulls from live database
    '''
    return await _list_histograms(database_name=chooseDatabase(isLive))


@query.field("getHistogram")
async def resolve_histogram(*_, id):
    return await _get_histogram(id=id, database_name=chooseDatabase())


@query.field("getHistograms")
async def resolve_histograms(*_, ids=None, names=None, types=None, minDate=None, maxDate=None, isLive=False):
    return await _filter_histograms(ids, names, types, minDate, maxDate, isLive)
