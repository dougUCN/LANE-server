import datetime

DATABASE = "live" # Devices and runfiles should be stored to the live database


deviceStatesFields = ['device', 'state', 'time']

runInputField = ['name', 'qOrder','startTime', 
                'deviceStates', 'status', 'runTime']

deviceInputField = ['name',  'states',  'currentState', 'isOnline']

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

def clean_run_input( run ):
    '''Processes run input from graphQL
    '''
    runInput = {}
    for field in runInputField:
        runInput[field] = run.get( field )

    if runInput['deviceStates'] is not None:
        check_device_states( runInput['deviceStates'] )

    if runInput['qOrder'] is None:
        runInput['qOrder'] = 0
    if runInput['status'] is None:
        runInput['status'] = EnumState['QUEUED']

    return runInput

def check_device_states( deviceStates ):
    '''Checks to make sure device states is in an expected format
    '''
    for field in deviceStatesFields:
        if len(deviceStates[field]) != len(deviceStates[ deviceStatesFields[0] ] ):
            ValueError(f'Device state fields {deviceStatesFields} are not all the same length')   

def clean_device_input( device ):
    '''Processes device input from graphQL
    '''
    deviceInput = {}
    for field in deviceInputField:
        deviceInput[field] = device.get( field )

    if deviceInput['isOnline'] is None:
        deviceInput['isOnline'] = False

    if deviceInput['states']:
        deviceInput['states'] = list_to_str(deviceInput['states'])

    return deviceInput

def clean_live_run_output( run ):
    '''Calculates time elapsed for a live run and returns the run with the new property
    '''
    run.timeElapsed = (datetime.datetime.now() - run.startTime).total_seconds()
    return run

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