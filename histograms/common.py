"""
Common histogram-related functions
"""

def histogram_payload( message, success ):
    return {'message': message, 
            'success': success,
            }

def clean_hist_input( hist ):
    '''Takes histogram input from graphQL resolver and prepares to put it into the database
    '''
    nbins = hist.get('nbins')
    data = hist.get('data')
    if (nbins is None) and data:
        nbins = len(data)
    elif data is None:
        nbins = 0 
    return {
            'id': hist['id'],
            'data': int_to_commsep( data ),
            'nbins': nbins,
            'type': hist.get('type'),
            'database': chooseDatabase( hist.get('isLive') ),
            }

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
    return [int(x) for x in string.split(',')]