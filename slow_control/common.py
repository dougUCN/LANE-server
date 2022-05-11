import datetime

from ariadne import EnumType

DATABASE = "live" # Devices and runfiles should be stored to the live database


deviceStatesFields = ['device', 'state', 'time']

#               Graphql: Django
runInputField = {'name': 'name', 
                'qOrder': 'q_order', 
                'startTime': 'start_time',
                'deviceStates': 'device_states',
                'status': 'status', 
                'runTime': 'runtime',
                }

#                   Graphql: Django
deviceInputField = {'name' : 'name',
                    'states': 'states',
                    'currentState': 'current_state', 
                    'isOnline': 'is_online'}

#           Graphql:  Django
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
    for key, django in runInputField.items():
        runInput[django] = run.get( key )

    if runInput['device_states'] is not None:
        check_device_states( runInput['device_states'] )

    if runInput['q_order'] is None:
        runInput['q_order'] = 0
    if runInput['status'] is None:
        runInput['status'] = EnumState['QUEUED']

    return runInput

def check_device_states( deviceStates ):
    '''Checks to make sure device states is in an expected format
    '''
    for key in deviceStatesFields:
        if len(deviceStates[key]) != len(deviceStates[ deviceStatesFields[0] ] ):
            ValueError(f'Device state fields {deviceStatesFields} are not all the same length')   

def clean_device_input( device ):
    '''Processes device input from graphQL
    '''
    deviceInput = {}
    for graphql, django in deviceInputField.items():
        deviceInput[django] = device.get( graphql )

    if deviceInput['is_online'] is None:
        deviceInput['is_online'] = False

    return deviceInput

def clean_live_run_output( run ):
    '''Calculates time stamp for a live run and outputs in expected graphql format
    '''
    # runOutput = {}
    # for graphql, django in runInputField.items():
    #     runOutput[graphql] = getattr( run, django )

    # # Calculate elapsed time for live runs
    # if (runOutput['status'] == EnumType['RUNNING']) and (runOutput['startTime'] is not None):
    #     runOutput['timeElapsed'] = (datetime.datetime.now() - runOutput['startTime']).total_seconds()
    # else:
    #     runOutput['timeElapsed'] = None

    # return runOutput
    run.timeElapsed = (datetime.datetime.now() - run.start_time).total_seconds()
    return run