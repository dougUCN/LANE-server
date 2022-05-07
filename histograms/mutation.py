from ariadne import MutationType
from .models import Histogram

from channels.db import database_sync_to_async

from .common import  histogram_payload, clean_hist_input, chooseDatabase


"""
Asynchronous database access 
"""

@database_sync_to_async
def _create_histogram( clean_hist, database_name):
    new_hist = Histogram(id = clean_hist['id'], data=clean_hist['data'],
                             nbins=clean_hist['nbins'], type=clean_hist['type'],)
    new_hist.save(using = database_name)
    return True

@database_sync_to_async
def _update_histogram( clean_hist, database_name):
    in_database = Histogram.objects.using(database_name).get(id=clean_hist['id'])
    if clean_hist['data']:
        in_database.data = clean_hist['data']
        in_database.nbins = clean_hist['nbins']
    if clean_hist['type']:
        in_database.type = clean_hist['type']
    in_database.save(using = database_name)
    return True


@database_sync_to_async
def _delete_histogram( id, database_name):
    Histogram.objects.using( database_name ).get(id=id).delete()
    return True

"""
Mutations
"""

mutation = MutationType()

@mutation.field("createHistogram")
async def create_histogram(*_, hist):
    clean_hist = clean_hist_input(hist)
    status = await _create_histogram( clean_hist, database_name= clean_hist['database'])
    return histogram_payload(f'created hist {clean_hist["id"]}', success=status)


@mutation.field("updateHistogram")
async def update_histogram(*_, hist):
    '''Updates non-empty fields from hist object'''
    clean_hist = clean_hist_input(hist)
    status = await _update_histogram( clean_hist, database_name= clean_hist['database'])
    return histogram_payload(f'updated hist {clean_hist["id"]}', success=status)

@mutation.field("deleteHistogram")
async def delete_histogram(*_, id, isLive=False):
    status = await _delete_histogram( id, database_name=chooseDatabase(isLive) )
    return histogram_payload(message = f'deleted hist {id}', success=status)


