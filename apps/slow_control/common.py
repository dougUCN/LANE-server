from django.utils import timezone
import uuid

DATABASE = "live"  # Devices and RunConfigs should be stored to the live database

MAX_RUN_CONFIGS = 20  # Max number of run configs allowed in the DB

# Fields as defined in the graphql schema as inputs for mutations

runConfigInputField = ['name', 'steps', 'priority', 'runConfigStatus', 'totalTime', 'lastLoaded', 'lastSaved']

deviceInputField = ['name', 'deviceOptions', 'isOnline']

RunState = {
    "QUEUED": "Queued",
    "RUNNING": "Running",
    "COMPLETED": "Completed",
    "READY": "Ready",
    "RUNTIME_ERROR": "RuntimeError",
    "STOPPED": "Stopped",
    "INVALID": "Invalid",
}

DeviceOption = {
    "SELECT_ONE": "SelectOne",
    "SELECT_MANY": "SelectMany",
    "USER_INPUT": "UserInput",
}


def run_config_payload(id, message, success, modified):
    return {
        'id': id,
        'message': message,
        'success': success,
        'modifiedRunConfig': modified,
    }


def device_payload(message, success, modified):
    return {
        'message': message,
        'success': success,
        'modifiedDevice': modified,
    }


def slow_control_payload(message, success):
    return {
        'message': message,
        'success': success,
    }


def clean_run_config_input(run, update=False):
    '''Processes run input from graphQL
    If `update` flag is specified, fields with None will stay None
    to avoid overriding existing entries with defaults
    '''
    runInput = {}
    for field in runConfigInputField:
        runInput[field] = run.get(field)

    if not update and runInput['totalTime'] < 0:
        raise ValueError('totalTime cannot be negative')

    if (runInput['priority'] is None) and not update:
        # On creation, Ensure each run config has a default priority of 0
        runInput['priority'] = 0
    if (runInput['runConfigStatus'] is None) and not update:
        # On creation, assign runConfigStatus INVALID or READY depending on if steps exist
        if runInput['steps']:
            runInput['runConfigStatus'] = {'status': RunState['READY'], 'messages': []}
        else:
            runInput['runConfigStatus'] = {
                'status': RunState['INVALID'],
                'messages': ['Invalid RunConfig: missing "steps". To add "steps," edit the RunConfig'],
            }
    if runInput['steps']:
        # Sort steps by time of execution
        runInput['steps'] = sorted(runInput['steps'], key=lambda step: step['time'])
        for step in runInput['steps']:
            # Ensure that each runconfig step has a uuid
            step.setdefault('id', str(uuid.uuid4()))
            # Input checking deviceOptions field
            try:
                if step['deviceOption']['deviceOptionType'] == DeviceOption['SELECT_ONE']:
                    if len(step['deviceOption']['selected']) != 1:
                        raise ValueError('deviceOption SELECT_ONE requires len(selected) = 1')
                    if not step['deviceOption']['options']:
                        raise ValueError('deviceOption SELECT_ONE requires `options` to be specified')
                elif step['deviceOption']['deviceOptionType'] == DeviceOption['SELECT_MANY']:
                    if len(step['deviceOption']['selected']) < 1:
                        raise ValueError('deviceOption SELECT_MANY requires len(selected) > 1')
                    if not step['deviceOption']['options']:
                        raise ValueError('deviceOption SELECT_MANY requires `options` to be specified')
                elif step['deviceOption']['deviceOptionType'] == DeviceOption['USER_INPUT']:
                    if len(step['deviceOption']['selected']) != 1:
                        raise ValueError('deviceOption USER_INPUT requires len(selected) = 1')
                else:
                    raise ValueError('deviceOption must be SELECT_ONE, SELECT_MANY, or USER_INPUT')
            except KeyError:
                raise KeyError(f'Step {step["id"]} requires the `selected` field to be filled')
    # Update lastSaved metadata
    runInput['lastSaved'] = timezone.now()

    return runInput


def clean_device_input(device, update=False):
    '''Processes device input from graphQL
    If `update` flag is specified, fields with None will stay None
    to avoid overriding existing entries with defaults
    '''
    deviceInput = {}
    for field in deviceInputField:
        deviceInput[field] = device.get(field)

    if (deviceInput['isOnline'] is None) and not update:
        deviceInput['isOnline'] = False

    return deviceInput
