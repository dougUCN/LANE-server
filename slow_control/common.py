import datetime
from django.utils.timezone import make_aware

DATABASE = "live" # Devices and runfiles should be stored to the live database


# Fields as defined in the graphql schema
deviceStatesFields = ['device', 'state', 'time']

runInputField = ['name', 'qOrder','startTime', 
                'deviceStates', 'status', 'runTime']

deviceInputField = ['name',  'states',  'currentState', 'isOnline']

# These fields are string fields in the django model
# that may be defined as None on instantiation.
# These will be replaced with an empty str
device_string_field = ['states', 'currentState']
run_string_field = ['status']

EnumState = {
            "QUEUED": "Queued",
            "RUNNING": "Running",
            "COMPLETED": "Completed",
            }

def run_payload( message, success ):
    return {'message': message, 
            'success': success,
            }

def device_payload( message, success ):
    return {'message': message, 
            'success': success,
            }

def clean_run_input( run , update=False):
    '''Processes run input from graphQL
    If `update` flag is specified, fields with None will stay None
    to avoid overriding existing entries with defaults
    '''
    runInput = {}
    for field in runInputField:
        runInput[field] = run.get( field )

    if runInput['deviceStates'] is not None:
        check_device_states( runInput['deviceStates'] )

    if (runInput['qOrder'] is None) and not update:
        runInput['qOrder'] = 0
    if (runInput['status'] is None) and not update:
        runInput['status'] = EnumState['QUEUED']
    elif (runInput['status'] is EnumState['RUNNING']) and (runInput['startTime'] is None):
        raise ValueError('When setting run status to `RUNNING` you must specify the start time')

    return runInput

def check_device_states( deviceStates ):
    '''Checks to make sure device states is in an expected format
    '''
    for field in deviceStatesFields:
        if len(deviceStates[field]) != len(deviceStates[ deviceStatesFields[0] ] ):
            raise ValueError(f'DeviceStatesInput fields {deviceStatesFields} are not all the same length')   

def clean_device_input( device , update=False):
    '''Processes device input from graphQL
    If `update` flag is specified, fields with None will stay None
    to avoid overriding existing entries with defaults
    '''
    deviceInput = {}
    for field in deviceInputField:
        deviceInput[field] = device.get( field )

    if (deviceInput['isOnline'] is None) and not update:
        deviceInput['isOnline'] = False

    if deviceInput['states']:
        deviceInput['states'] = list_to_str(deviceInput['states'])

    return deviceInput

def calc_time_elapsed( run ):
    '''Calculates time elapsed for a live run and returns value in seconds
    '''
    return (make_aware(datetime.datetime.now()) - run.startTime).total_seconds()
    

def list_to_str( list_of_strs ):
    '''Converts a list of strings into a comma separated string
    '''
    if list_of_strs:
        return ','.join([i for i in list_of_strs])
    else:
        return None

def str_to_list( string ):
    '''Converts a string of comma separated strings into a list
    '''
    if string == '':
        return []
    else:
        return [i for i in string.split(',')]