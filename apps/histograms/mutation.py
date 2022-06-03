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

"""
Asynchronous database access 
"""


@database_sync_to_async
def _create_histogram(clean_hist, database_name):
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in hist_string_field:
        if clean_hist[field] is None:
            clean_hist[field] = ''

    # Update HistTable entry
    table_entry = HistTable.objects.using(STATIC_DATABASE).filter(name=clean_hist['name'])
    if table_entry:  # Evaluating queryset here instead of using .exists() is more efficient in this case
        table_entry.histIDs.append(clean_hist['id'])
        table_entry.save(using=STATIC_DATABASE)
    else:
        # If this is the first histogram with a certain name,
        # create a new entry in the HistTable
        new_table_entry = HistTable(
            name=clean_hist['name'],
            histIDs=[clean_hist['id']],
            isLive=(database_name is LIVE_DATABASE),
        )
        new_table_entry.save(using=STATIC_DATABASE)

    # Remove the isLive argument from the dict so django model
    # does not throw any error at unexpected kwarg
    try:
        del clean_hist['isLive']
    except KeyError:
        pass

    # Create new histogram
    new_hist = Histogram(**clean_hist)
    new_hist.save(using=database_name)
    return True


@database_sync_to_async
def _update_histogram(clean_hist, database_name):
    '''Returns (updated fields, success)'''
    in_database = Histogram.objects.using(database_name).get(id=clean_hist['id'])

    updatedFields = []
    for attr in clean_hist.keys():
        if attr == 'id':  # Avoid altering PK
            continue
        elif (clean_hist[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_hist[attr])
            updatedFields.append(attr)
    in_database.save(using=database_name)
    return (updatedFields, True)


@database_sync_to_async
def _delete_histogram(id, database_name):
    to_delete = Histogram.objects.using(database_name).get(id=id)

    # Update HistTable entry
    table_entry = HistTable.objects.using(STATIC_DATABASE).filter(name=to_delete.name)
    table_entry.histIDs.remove(id)
    if not table_entry.histIDs:
        table_entry.delete()

    to_delete.delete()
    return True


"""
Mutations
"""

mutation = MutationType()


@mutation.field("createHistogram")
async def create_histogram(*_, hist):
    clean_hist = clean_hist_input(hist)
    status = await _create_histogram(clean_hist, database_name=chooseDatabase(clean_hist['isLive']))
    return histogram_payload(f'created hist {clean_hist["id"]}', success=status)


@mutation.field("updateHistogram")
async def update_histogram(*_, hist):
    '''Updates non-empty fields from hist object'''
    clean_hist = clean_hist_input(hist)
    updatedFields, status = await _update_histogram(clean_hist, database_name=chooseDatabase(clean_hist['isLive']))
    return histogram_payload(f'Updated fields {updatedFields}', success=status)


@mutation.field("deleteHistogram")
async def delete_histogram(*_, id, isLive=False):
    status = await _delete_histogram(id, database_name=chooseDatabase(isLive))
    return histogram_payload(message=f'deleted hist {id}', success=status)
