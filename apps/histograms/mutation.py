from ariadne import MutationType
from .models import Histogram, HistTable
from channels.db import database_sync_to_async

from .common import (
    histogram_payload,
    clean_hist_input,
    chooseDatabase,
    hist_string_field,
    STATIC_DATABASE,
    LIVE_DATABASE,
)

from .query import _get_histogram

"""
Asynchronous database access 
"""


@database_sync_to_async
def _create_histogram(clean_hist, database_name):
    """Returns (created_histogram, True)"""
    # Remove the isLive argument from the dict so django model
    # does not throw any error at unexpected kwarg
    try:
        del clean_hist['isLive']
    except KeyError:
        pass

    # Create new histogram
    new_hist = Histogram(**clean_hist)
    new_hist.save(using=database_name)
    return new_hist, True


@database_sync_to_async
def _update_histogram(clean_hist, database_name):
    '''Returns (updated_histogram, updated_fields, success)'''
    in_database = Histogram.objects.using(database_name).get(id=clean_hist['id'])

    updatedFields = []
    for attr in clean_hist.keys():
        if attr == 'id':  # Avoid altering PK
            continue
        elif (clean_hist[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_hist[attr])
            updatedFields.append(attr)
    in_database.save(using=database_name)
    return (in_database, updatedFields, True)


@database_sync_to_async
def _delete_histogram(id, database_name):
    to_delete = Histogram.objects.using(database_name).get(id=id)

    # Update HistTable entry
    table_entry = HistTable.objects.using(STATIC_DATABASE).get(name=to_delete.name)
    table_entry.histIDs.remove(id)
    if not table_entry.histIDs:
        table_entry.delete()
    else:
        table_entry.save(using=STATIC_DATABASE)

    to_delete.delete()
    return True


@database_sync_to_async
def _update_hist_table_entry(clean_hist, database_name):
    """Update HistTable entry"""
    try:
        table_entry = HistTable.objects.using(STATIC_DATABASE).get(name=clean_hist['name'])
        table_entry.histIDs.append(clean_hist['id'])
        table_entry.isLive = database_name is LIVE_DATABASE
        table_entry.save(using=STATIC_DATABASE)
    except HistTable.DoesNotExist:
        # If this is the first histogram with a certain name,
        # create a new entry in the HistTable
        new_table_entry = HistTable(
            name=clean_hist['name'],
            histIDs=[clean_hist['id']],
            isLive=(database_name is LIVE_DATABASE),
        )
        new_table_entry.save(using=STATIC_DATABASE)
    return True


"""
Mutations
"""

mutation = MutationType()


@mutation.field("createHistogram")
async def create_histogram(*_, hist):
    clean_hist = clean_hist_input(hist)
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in hist_string_field:
        if clean_hist[field] is None:
            clean_hist[field] = ''
    table_status = await _update_hist_table_entry(clean_hist, database_name=chooseDatabase(clean_hist['isLive']))
    modified, create_status = await _create_histogram(clean_hist, database_name=chooseDatabase(clean_hist['isLive']))
    return histogram_payload(modified=modified, message=f'created hist {clean_hist["id"]}', success=all([create_status, table_status]))


@mutation.field("updateHistogram")
async def update_histogram(*_, hist):
    '''Updates non-empty fields from hist object'''
    clean_hist = clean_hist_input(hist)
    modified, updatedFields, status = await _update_histogram(clean_hist, database_name=chooseDatabase(clean_hist['isLive']))
    return histogram_payload(modified=modified, message=f'Updated fields {updatedFields}', success=status)


@mutation.field("deleteHistogram")
async def delete_histogram(*_, id, isLive=False):
    modified = await _get_histogram(id, database_name=chooseDatabase(isLive))
    status = await _delete_histogram(id, database_name=chooseDatabase(isLive))
    return histogram_payload(modified=modified, message=f'deleted hist {id}', success=status)
