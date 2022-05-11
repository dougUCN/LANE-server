from ariadne import MutationType
from .models import Runfile, Device

from channels.db import database_sync_to_async

from .common import  (run_payload, device_payload, DATABASE,
                        clean_run_input, clean_device_input,
                        runInputField, deviceInputField)

from .messaging import slowControlCmd, COMMAND

device_string_field = ['states', 'currentState']
run_string_field = ['status']

"""
Asynchronous database access 
"""

@database_sync_to_async
def _create_run( clean_run ):
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in run_string_field:
        if clean_run[field] is None:
            clean_run[field] = ''
    new_run = Runfile( **clean_run)
    new_run.save(using = DATABASE)
    return True

@database_sync_to_async
def _update_run( clean_run ):
    '''Returns (updated fields, success)'''
    in_database = Runfile.objects.using( DATABASE ).get(name=clean_run['name'])
    updatedFields = []
    for attr in runInputField:
        if attr == 'name':
            continue
        elif (clean_run[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_run[attr])
            updatedFields.append(attr)
    return (updatedFields, True)


@database_sync_to_async
def _delete_run( name ):
    Runfile.objects.using( DATABASE ).get(name=name).delete()
    return True

@database_sync_to_async
def _create_device( clean_device ):
    # Django does not like saving null values in the string fields
    # and prefers blank strs
    for field in device_string_field:
        if clean_device[field] is None:
            clean_device[field] = ''
    new_device = Device( **clean_device)
    new_device.save(using = DATABASE)
    return True

@database_sync_to_async
def _update_device( clean_device ):
    '''Returns (updated fields, success)'''
    in_database = Device.objects.using( DATABASE ).get(name=clean_device['name'])
    updatedFields = []
    for attr in deviceInputField:
        if attr == 'name':
            continue
        elif (clean_device[attr] is not None) and hasattr(in_database, attr):
            setattr(in_database, attr, clean_device[attr])
            updatedFields.append(attr)
    return (updatedFields, True)

@database_sync_to_async
def _delete_device( name ):
    Device.objects.using( DATABASE ).get(name=name).delete()
    return True


"""
Run-related Mutations
"""

mutation = MutationType()

@mutation.field('createRun')
async def create_run(*_, run):
    clean_run = clean_run_input( run )
    status = await _create_run( clean_run )
    return run_payload(f'created run {clean_run["name"]}', success = status)

@mutation.field('updateRun')
async def update_run(*_, run):
    clean_run = clean_run_input( run )
    updatedFields, status = await _update_run( clean_run )
    return run_payload(f'Updated fields {updatedFields}', success = status)

@mutation.field('deleteRun')
async def delete_run(*_, name):
    status = await _delete_run( name )
    return run_payload(f'deleted runfile {name}', success = status)

@mutation.field('clearRuns')
async def clear_runs(*_):
    status = slowControlCmd( COMMAND['CLEAR'] )
    return run_payload(f'Clear command sent', success = status)

@mutation.field('startRuns')
async def start_runs(*_):
    status = slowControlCmd( COMMAND['START'] )
    return run_payload(f'Start command sent', success = status)

@mutation.field('stopRuns')
async def stop_runs(*_, stopAfterThisRun):
    if stopAfterThisRun:
        status = slowControlCmd( COMMAND['SOFT_STOP'] )
        return run_payload(f'Soft stop command sent', success = status)
    else:
        status = slowControlCmd( COMMAND['HARD_STOP'] )
        return run_payload(f'Hard stop command sent', success = status)

"""
Device-related Mutations
"""

@mutation.field('refreshDevices')
async def refresh_devices(*_):
    status = slowControlCmd( COMMAND['REFRESH'] )
    return device_payload(f'Refresh command sent', success = status)

@mutation.field('createDevice')
async def create_device(*_, device):
    clean_device = clean_device_input( device )
    status = await _create_device( clean_device )
    return device_payload(f'Device created', success = status)

@mutation.field('updateDevice')
async def update_device(*_, device):
    clean_device = clean_device_input( device )
    updatedFields, status = await _update_device( clean_device )
    return run_payload(f'Updated fields {updatedFields}', success = status)

@mutation.field('deleteDevice')
async def delete_delete(*_, name):
    status = await _delete_device( name )
    return device_payload(f'deleted device {name}', success = status)


