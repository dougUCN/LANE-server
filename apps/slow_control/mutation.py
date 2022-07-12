from ariadne import MutationType
from .models import RunConfig, Device

from django.utils import timezone
from channels.db import database_sync_to_async

from .common import (
    run_config_payload,
    device_payload,
    slow_control_payload,
    DATABASE,
    clean_run_config_input,
    clean_device_input,
    runConfigInputField,
    deviceInputField,
    RunState,
)

from .messaging import slowControlCmd, COMMAND

from .query import _filter_runs, _get_device, _get_run_config

"""
Asynchronous database access 
"""


@database_sync_to_async
def _create_run_config(clean_run):
    '''Returns (created_run_config, run_id, success)'''
    new_run = RunConfig(**clean_run)
    new_run.save(using=DATABASE)
    return new_run, new_run.id, True


@database_sync_to_async
def _update_run_config(id, clean_run):
    '''Returns (updated_run_config, run_id, updated fields, success)'''
    in_database = RunConfig.objects.using(DATABASE).get(pk=id)
    updatedFields = []
    for attr in runConfigInputField:
        if (clean_run[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_run[attr])
            updatedFields.append(attr)
    in_database.save(using=DATABASE)
    return in_database, in_database.id, updatedFields, True


@database_sync_to_async
def _delete_run_config(id):
    '''Returns True on success'''
    RunConfig.objects.using(DATABASE).get(pk=id).delete()
    return True


@database_sync_to_async
def _create_device(clean_device):
    '''Returns (created_device, true)'''
    new_device = Device(**clean_device)
    new_device.save(using=DATABASE)
    return new_device, True


@database_sync_to_async
def _update_device(clean_device):
    '''Returns (updated_device, updated fields, success)'''
    in_database = Device.objects.using(DATABASE).get(name=clean_device['name'])
    updatedFields = []
    for attr in deviceInputField:
        if attr == 'name':  # Device name is effectively the PK so avoid changing
            continue
        elif (clean_device[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_device[attr])
            updatedFields.append(attr)
    in_database.save(using=DATABASE)
    return (in_database, updatedFields, True)


@database_sync_to_async
def _delete_device(name):
    '''Returns True on success'''
    Device.objects.using(DATABASE).get(name=name).delete()
    return True


"""
Run Config-related Mutations
"""

mutation = MutationType()


@mutation.field('createRunConfig')
async def create_run_config(*_, runConfig):
    clean_run_config = clean_run_config_input(runConfig)
    modified, id, status = await _create_run_config(clean_run_config)
    return run_config_payload(modified=modified, id=id, message=f'created run {clean_run_config["name"]}', success=status)


@mutation.field('updateRunConfig')
async def update_run_config(*_, runConfig):
    clean_run = clean_run_config_input(runConfig, update=True)
    modified, id, updatedFields, status = await _update_run_config(runConfig['id'], clean_run)
    return run_config_payload(modified=modified, id=id, message=f'Updated fields {updatedFields}', success=status)


@mutation.field('deleteRunConfig')
async def delete_run_config(*_, id):
    modified = await _get_run_config(id)
    status = await _delete_run_config(id)
    return run_config_payload(modified=modified, id=id, message=f'deleted runfile with id: {id}', success=status)


@mutation.field('loadRunConfig')
async def load_run_config(*_, id):
    queuedRunConfig = {key: None for key in runConfigInputField}
    queuedRunConfig['runConfigStatus'] = {'status': RunState['QUEUED'], 'messages': []}
    queuedRunConfig['lastLoaded'] = timezone.now()  # Timezone aware version of datetime.now

    # If runs are already queued, update the run to a lower priority
    inDatabase = await _filter_runs()
    existingIDs = []
    existingPriority = []
    for conf in inDatabase:
        try:
            if conf['runConfigStatus']['status'] == RunState['QUEUED']:
                existingIDs.append(conf.id)
                existingPriority.append(conf.priority)
        except KeyError:
            pass

    if existingIDs:
        if int(id) in existingIDs:
            raise ValueError(f'RunConfig ID {id} is already {RunState["QUEUED"]}')
        queuedRunConfig['priority'] = max(existingPriority) + 1
    else:
        queuedRunConfig['priority'] = 0

    _, _, status = await _update_run_config(id, queuedRunConfig)

    return slow_control_payload(message=f'Set RunConfig {id} to {RunState["QUEUED"]} at priority {queuedRunConfig["priority"]}', success=status)


"""
Slow Control Communication Mutations
"""


@mutation.field('clearRuns')
async def clear_runs(*_):
    """Message slow control the CLEAR_RUNS comm"""
    comm_status = slowControlCmd(COMMAND['CLEAR_RUNS'])
    return slow_control_payload(f'Sent {COMMAND["CLEAR_RUNS"]} to slow control', success=comm_status)


@mutation.field('stopRuns')
async def stop_runs(*_, stopAfterThisRun):
    if stopAfterThisRun:
        comm_status = slowControlCmd(COMMAND['SOFT_STOP'])
        return slow_control_payload(f'Sent {COMMAND["SOFT_STOP"]} to slow control', success=comm_status)
    else:
        comm_status = slowControlCmd(COMMAND['HARD_STOP'])
        return slow_control_payload(f'Sent {COMMAND["HARD_STOP"]} to slow control', success=comm_status)


@mutation.field('refreshDevices')
async def refresh_devices(*_):
    comm_status = slowControlCmd(COMMAND['REFRESH_DEVICES'])
    return slow_control_payload(f'Sent {COMMAND["REFRESH_DEVICES"]} to slow control', success=comm_status)


"""
Device-related Mutations
"""


@mutation.field('createDevice')
async def create_device(*_, device):
    clean_device = clean_device_input(device)
    modified, status = await _create_device(clean_device)
    return device_payload(modified=modified, message=f'Device created', success=status)


@mutation.field('updateDevice')
async def update_device(*_, device):
    clean_device = clean_device_input(device, update=True)
    modified, updatedFields, status = await _update_device(clean_device)
    return device_payload(modified=modified, message=f'Updated fields {updatedFields}', success=status)


@mutation.field('deleteDevice')
async def delete_delete(*_, name):
    modified = await _get_device(name)
    status = await _delete_device(name)
    return device_payload(modified=modified, message=f'deleted device {name}', success=status)
