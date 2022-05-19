from ariadne import MutationType
from .models import Runfile, Device

from channels.db import database_sync_to_async

from .common import (
    run_payload,
    device_payload,
    DATABASE,
    clean_run_input,
    clean_device_input,
    runInputField,
    deviceInputField,
    EnumState,
    run_string_field,
    device_string_field,
)

from .messaging import slowControlCmd, COMMAND

from .query import _filter_runs

"""
Asynchronous database access 
"""


@database_sync_to_async
def _create_run(clean_run):
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in run_string_field:
        if clean_run[field] is None:
            clean_run[field] = ''
    new_run = Runfile(**clean_run)
    new_run.save(using=DATABASE)
    return True


@database_sync_to_async
def _update_run(id, clean_run):
    '''Returns (updated fields, success)'''
    in_database = Runfile.objects.using(DATABASE).get(pk=id)
    updatedFields = []
    for attr in runInputField:
        if (clean_run[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_run[attr])
            updatedFields.append(attr)
    in_database.save(using=DATABASE)
    return (updatedFields, True)


@database_sync_to_async
def _delete_run(id):
    Runfile.objects.using(DATABASE).get(pk=id).delete()
    return True


@database_sync_to_async
def _create_device(clean_device):
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in device_string_field:
        if clean_device[field] is None:
            clean_device[field] = ''
    new_device = Device(**clean_device)
    new_device.save(using=DATABASE)
    return True


@database_sync_to_async
def _update_device(clean_device):
    '''Returns (updated fields, success)'''
    in_database = Device.objects.using(DATABASE).get(name=clean_device['name'])
    updatedFields = []
    for attr in deviceInputField:
        if attr == 'name':  # Device name is effectively the PK so avoid changing
            continue
        elif (clean_device[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_device[attr])
            updatedFields.append(attr)
    in_database.save(using=DATABASE)
    return (updatedFields, True)


@database_sync_to_async
def _delete_device(name):
    Device.objects.using(DATABASE).get(name=name).delete()
    return True


"""
Run-related Mutations
"""

mutation = MutationType()


@mutation.field('createRun')
async def create_run(*_, run):
    clean_run = clean_run_input(run)
    status = await _create_run(clean_run)
    return run_payload(f'created run {clean_run["name"]}', success=status)


@mutation.field('updateRun')
async def update_run(*_, id, run):
    clean_run = clean_run_input(run, update=True)
    updatedFields, status = await _update_run(id, clean_run)
    return run_payload(f'Updated fields {updatedFields}', success=status)


@mutation.field('deleteRun')
async def delete_run(*_, id):
    status = await _delete_run(id)
    return run_payload(f'deleted runfile with id: {id}', success=status)


@mutation.field('clearRuns')
async def clear_runs(*_):
    """Message slow control the CLEAR comm and delete Queued/Completed runs from the DB"""
    comm_status = slowControlCmd(COMMAND['CLEAR'])
    for state in [EnumState['QUEUED'], EnumState['COMPLETED']]:
        filtered_runs = await _filter_runs(names=None, minStartDate=None, maxStartDate=None, minSubDate=None, maxSubDate=None, status=state)
        for run in filtered_runs:
            await _delete_run(run.id)

    return run_payload(f'Queued and Completed runs cleared in DB and slow control', success=comm_status)


@mutation.field('startRuns')
async def start_runs(*_):
    status = slowControlCmd(COMMAND['START'])
    return run_payload(f'Start command sent', success=status)


@mutation.field('stopRuns')
async def stop_runs(*_, stopAfterThisRun):
    if stopAfterThisRun:
        status = slowControlCmd(COMMAND['SOFT_STOP'])
        return run_payload(f'Soft stop command sent', success=status)
    else:
        status = slowControlCmd(COMMAND['HARD_STOP'])
        return run_payload(f'Hard stop command sent', success=status)


"""
Device-related Mutations
"""


@mutation.field('refreshDevices')
async def refresh_devices(*_):
    status = slowControlCmd(COMMAND['REFRESH'])
    return device_payload(f'Refresh command sent', success=status)


@mutation.field('createDevice')
async def create_device(*_, device):
    clean_device = clean_device_input(device)
    status = await _create_device(clean_device)
    return device_payload(f'Device created', success=status)


@mutation.field('updateDevice')
async def update_device(*_, device):
    clean_device = clean_device_input(device, update=True)
    updatedFields, status = await _update_device(clean_device)
    return run_payload(f'Updated fields {updatedFields}', success=status)


@mutation.field('deleteDevice')
async def delete_delete(*_, name):
    status = await _delete_device(name)
    return device_payload(f'deleted device {name}', success=status)
