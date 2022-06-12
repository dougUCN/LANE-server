from ariadne import QueryType
from .models import Histogram, HistTable
from channels.db import database_sync_to_async
from cursor_pagination import CursorPaginator
from .common import chooseDatabase, STATIC_DATABASE

""" Asynchronous generator for database access 
Note that we cannot pass querysets out from the generator, 
so we must evaluate the query set before returning
"""


@database_sync_to_async
def _get_histogram(id, database_name):
    return Histogram.objects.using(database_name).get(id=id)


@database_sync_to_async
def _filter_histograms(ids, names, types, minDate, maxDate, isLive):
    """Applies filters onto queryset"""
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


@database_sync_to_async
def _paginate_hist_table(first, after):
    """Paginates HistTable entries"""
    queryset = HistTable.objects.using(STATIC_DATABASE).all()
    # Order entries by descending order of creation date
    # (hence the `-` character)
    paginator = CursorPaginator(queryset, ordering=('-created',))

    # For some reason, CursorPaginator counts the entry of the last cursor as an entry
    if after:
        page = paginator.page(first=first + 1, after=after)
        pageIndex = 1
    else:
        page = paginator.page(first=first)
        pageIndex = 0

    if page:
        endCursor = paginator.cursor(page[-1])
        hasNextPage = page.has_next
    else:
        endCursor = None
        hasNextPage = False

    pageInfo = {'hasNextPage': hasNextPage, 'endCursor': endCursor}
    edges = [{'node': p, 'cursor': paginator.cursor(p)} for p in page[pageIndex:]]
    return {'edges': edges, 'pageInfo': pageInfo}


@database_sync_to_async
def _get_latest_hist_table_entry():
    """Returns the latest HistTable entry"""
    return HistTable.objects.using(STATIC_DATABASE).latest('created')


"""
Queries
"""

query = QueryType()


@query.field("getHistogram")
async def resolve_histogram(*_, id, isLive=False):
    return await _get_histogram(id=id, database_name=chooseDatabase(isLive))


@query.field("getHistograms")
async def resolve_histograms(*_, ids=None, names=None, types=None, minDate=None, maxDate=None, isLive=False):
    return await _filter_histograms(ids, names, types, minDate, maxDate, isLive)


@query.field("getHistTableEntries")
async def resolve_hist_table_entries(*_, first=100, after=None):
    return await _paginate_hist_table(first, after)
