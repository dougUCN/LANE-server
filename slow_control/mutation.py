from ariadne import MutationType
from .models import Runfile, Device

from channels.db import database_sync_to_async

from .common import  (run_payload, device_payload, DATABASE,
                        clean_run_input, clean_device_input)

from .messaging import slowControlCmd, COMMAND


"""
Asynchronous database access 
"""

@database_sync_to_async
def _create_run( clean_run ):
    new_run = Runfile( **clean_run)
    new_run.save(using = DATABASE)
    return True

@database_sync_to_async
def _update_run( clean_run ):
    in_database = Runfile.objects.using( DATABASE ).get(name=clean_run['name'])
    return True


@database_sync_to_async
def _delete_run( name ):
    Runfile.objects.using( DATABASE ).get(name=name).delete()
    return True

@database_sync_to_async
def _create_device( clean_device ):
    new_device = Device( **clean_device)
    new_device.save(using = DATABASE)
    return True

@database_sync_to_async
def _update_device( clean_device ):
    in_database = Runfile.objects.using( DATABASE ).get(name=clean_device['name'])
    return True

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
    status = await _update_run( clean_run )
    return run_payload(f'', success = status)

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
    status = await _update_device( clean_device )
    return device_payload(f'Device updated', success = status)

@mutation.field('deleteDevice')
async def delete_delete(*_, name):
    status = await _delete_device( name )
    return device_payload(f'deleted device {name}', success = status)


