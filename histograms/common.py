"""
Common histogram-related functions
"""

# Input fields as defined by graphql schema
histInputField = ['id', 'name', 'data', 'xrange', 'yrange', 'type', 'isLive']

# These fields are string fields in the django model
# that may be defined as None on instantiation.
# These will be replaced with an empty str
hist_string_field = ['name', 'type']


def histogram_payload(message, success):
    return {
        'message': message,
        'success': success,
    }


def clean_hist_input(hist):
    '''Takes histogram input from graphQL resolver and prepares to put it into the database'''
    histInput = {}
    for field in histInputField:
        histInput[field] = hist.get(field)
    if histInput['data']:
        histInput['len'] = len(histInput['data'])

    return histInput


def chooseDatabase(isLive=None):
    '''Really janky way of choosing whether to write to live database or static database

    Defaults to `data` database for histograms
    '''
    if isLive:
        return "live"
    else:
        return "data"
