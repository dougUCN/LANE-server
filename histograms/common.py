"""
Common histogram-related functions
"""

# Input fields as defined by graphql schema
histInputField = ['id', 'name', 'x', 'y', 'type', 'isLive']

# These fields are string fields in the django model
# that may be defined as None on instantiation.
# These will be replaced with an empty str
hist_string_field = ['x', 'y', 'name', 'type']

def histogram_payload( message, success ):
    return {'message': message, 
            'success': success,
            }

def clean_hist_input( hist ):
    '''Takes histogram input from graphQL resolver and prepares to put it into the database
    '''
    histInput = {}
    for field in histInputField:
        histInput[field] = hist.get( field )

    histInput = get_length_data( histInput )

    # Convert x and y data list into strings
    if histInput['x']:
        histInput['x'] = int_to_commsep(histInput['x'])
    if histInput['y']:
        histInput['y'] = int_to_commsep(histInput['y'])

    return histInput

def clean_hist_output( hist ):
    '''Takes histogram from django model and outputs to graphql format'''
    hist.x = commsep_to_int( hist.x )
    hist.y = commsep_to_int( hist.y )
    return hist

def get_length_data( histInput ):
    '''Calculate length property from histogram input'''
    if (histInput['x'] is None) and (histInput['y'] is None):
        # If both x and y data values are not specified
        histInput['len'] = None
    elif histInput['x'] and histInput['y']:
        # If both x and y are defined
        histInput['len'] = len(histInput['y'])
        if len(histInput['x']) != histInput['len']:
            raise ValueError('Histogram x and y input lists not the same length')
    elif histInput['x'] and (histInput['y'] is None):
        # If x is specified but y is not
        histInput['len'] = len(histInput['x'])
    elif (histInput['x'] is none) and histInput['y']:
        # If y is specified but x is not
        histInput['len'] = len(histInput['y'])
    else:
        histInput['len'] = None

    return histInput


def chooseDatabase( isLive = None ):
    '''Really janky way of choosing whether to write to live database or static database

    Defaults to `data` database for histograms
    '''
    if isLive: 
        return "live"
    else:
        return "data"

def int_to_commsep( list_of_ints ):
    '''Converts a list of integers into a comma separated integer list
    '''
    if list_of_ints:
        return ','.join([str(i) for i in list_of_ints])
    else:
        return None

def commsep_to_int( string ):
    '''Converts a string of comma separated integers into a list of ints
    '''
    if string == '':
        return []
    else:
        return [int(x) for x in string.split(',')]