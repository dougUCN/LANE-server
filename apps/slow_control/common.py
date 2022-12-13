from django.utils import timezone

DATABASE = "data"  # Devices and RunConfigs should be stored to the static db

MAX_RUN_CONFIGS = 50  # Max number of run configs allowed in the DB

# Fields as defined in the graphql schema as inputs for mutations

runConfigInputField = ['name', 'steps', 'priority', 'runConfigStatus', 'totalTime', 'lastLoaded', 'lastSaved']
runConfigStepInputField = ['id', 'deviceName', 'deviceOptions', 'time', 'description']
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


def run_config_payload(message, success, modified):
    return {
        'message': message,
        'success': success,
        'modifiedRunConfig': modified,
    }


def steps_payload(message, success, modified, runConfigId):
    return {
        'message': message,
        'success': success,
        'modifiedStep': modified,
        'runConfigId': runConfigId,
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
        for step in runInput['steps']:
            step = clean_step_input(step)

    # Update lastSaved metadata
    runInput['lastSaved'] = timezone.now()

    return runInput


def clean_step_input(step):
    '''Ensure that each runconfig step has a uuid and a valid input
    Returns clean_step'''
    clean_step = {}
    for field in runConfigStepInputField:
        clean_step[field] = step.get(field)
    check_step_validity(step)
    return clean_step


def check_step_validity(step):
    '''Checks the validity of a RunConfigStep'''
    try:
        # Input checking deviceOptions field
        if hasattr(step, 'deviceOptions'):
            for deviceOption in step['deviceOptions']:
                if deviceOption['deviceOptionType'] == DeviceOption['SELECT_ONE']:
                    if len(deviceOption['selected']) != 1:
                        raise ValueError(f'Step {step["id"]} deviceOption SELECT_ONE requires len(selected) = 1')
                    if not deviceOption['options']:
                        raise ValueError(f'Step {step["id"]} deviceOption SELECT_ONE requires `options` to be specified')
                elif deviceOption['deviceOptionType'] == DeviceOption['SELECT_MANY']:
                    if len(deviceOption['selected']) < 1:
                        raise ValueError(f'Step {step["id"]} deviceOption SELECT_MANY requires len(selected) > 1')
                    if not deviceOption['options']:
                        raise ValueError(f'Step {step["id"]} deviceOption SELECT_MANY requires `options` to be specified')
                elif deviceOption['deviceOptionType'] == DeviceOption['USER_INPUT']:
                    if len(deviceOption['selected']) != 1:
                        raise ValueError(f'Step {step["id"]} deviceOption USER_INPUT requires len(selected) = 1')
                else:
                    raise ValueError('deviceOption must be SELECT_ONE, SELECT_MANY, or USER_INPUT')
    except KeyError as error:
        raise KeyError(f'Step {step["id"]} missing expected field {error}')


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
