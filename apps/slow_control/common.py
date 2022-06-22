import datetime
from django.utils.timezone import make_aware

DATABASE = "live"  # Devices and RunConfigs should be stored to the live database

MAX_RUN_CONFIGS = 20  # Max number of run configs allowed in the DB

# Fields as defined in the graphql schema as inputs for mutations

runConfigInputField = ['name', 'steps', 'priority', 'status', 'totalTime', 'lastLoaded']

deviceInputField = ['name', 'deviceOptions', 'isOnline']

RunState = {
    "QUEUED": "Queued",
    "RUNNING": "Running",
    "COMPLETED": "Completed",
    "NONE": "None",
    "ERROR": "Error",
    "STOPPED": "Stopped",
}

TimeFrame = {
    "BEFORE": "Before",
    "DURING": "During",
    "AFTER": "After",
}

DeviceOption = {
    "SELECT_ONE": "SelectOne",
    "SELECT_MANY": "SelectMany",
    "USER_INPUT": "UserInput",
}


def run_config_payload(id, message, success):
    return {
        'id': id,
        'message': message,
        'success': success,
    }


def device_payload(message, success):
    return {
        'message': message,
        'success': success,
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

    if (runInput['priority'] is None) and not update:
        runInput['priority'] = 0
    if (runInput['status'] is None) and not update:
        runInput['status'] = RunState['NONE']

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
