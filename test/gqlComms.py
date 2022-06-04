"""
Functions for communication with graphql endpoint via python
"""
from typing import Type
import requests
import json
import numpy as np
import datetime

ENDPOINT = 'http://127.0.0.1:8000/graphql/'


class NpEncoder(json.JSONEncoder):
    '''Allow json to dump numpy types
    https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
    '''

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool):
            return bool(obj)
        return super(NpEncoder, self).default(obj)


def dump_response(response):
    '''Dump a json response to str with indent 2'''
    return json.dumps(response, indent=2)


def make_replacements(string, replacements):
    for key, value in replacements.items():
        if isinstance(value, str) and (value[0] != '[') and (value[0] != '{'):
            string = string.replace(key, f'"{str(value)}"')
        elif isinstance(value, bool):
            string = string.replace(key, str(value).lower())
        elif value is None:
            string = string.replace(key, 'null')
        elif isinstance(value, list):
            string = string.replace(key, json.dumps(value, cls=NpEncoder))
        elif isinstance(value, dict):
            string = string.replace(key, dict_to_query(value))
        elif isinstance(value, datetime.datetime):
            string = string.replace(key, f'"{value.isoformat()}"')
        else:
            string = string.replace(key, str(value))
    return string


def check_response_errors(response):
    '''
    Check for the existence of errors in the graphql response json
    '''
    error = response.get("errors")
    if error is not None:
        raise RuntimeError(dump_response(error))
    return response


def make_query(query, url=ENDPOINT, headers=None):
    '''
    Sends a query to the URL. Returns a response json if successful
    '''
    request = requests.post(url, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return check_response_errors(request.json())
    else:
        raise Exception('Query failed to run by returning code of {}. {}'.format(request.status_code, query))


def toSvgStr(xList, yList):
    '''
    Takes two lists x and y and creates a string
    "[{x: x0, y: y0},
    {x: x1, y: y1},
    ...]"

    That is compatible for a graphql query string
    '''
    output = ['[']
    for x, y in zip(xList, yList):
        output.append(f'{{x:{x},y:{y}}},')
    output.append(']')

    return ''.join(output)


def toSvgCoords(xList, yList):
    '''
    Takes two lists x and y and creates a dictionary
    [{"x": x0, "y": y0},
    {"x": x1, "y": y1},
    ...]
    '''
    return [{'x': x, 'y': y} for (x, y) in zip(xList, yList)]


def dict_to_query(input):
    '''
    Basically removes quotes from any string keys in a dictionary

    TODO: Make recursive to apply to dicts of any depth
    '''
    if type(input) == dict:
        output = ['{']
        for key, value in input.items():
            output.append(f'{key}:{ dict_to_query(value) },')
        output.append('}')
        return ''.join(output)
    else:
        return input


def listHistograms(ids=None, names=None, minDate=None, maxDate=None, types=None, isLive=False):
    '''
    Returns a list of all histograms in the database
    '''
    replacements = {'$IDS': ids, '$NAMES': names, "$MINDATE": minDate, "$MAXDATE": maxDate, "$TYPES": types, "$ISLIVE": isLive}
    query = """query getHistograms{
                        getHistograms( 
                                ids: $IDS
                                names: $NAMES
                                minDate: $MINDATE,
                                maxDate: $MAXDATE,
                                types: $TYPES,
                                isLive: $ISLIVE
                                )
                            {
                                id
                            }
                        }"""
    query = make_replacements(query, replacements)
    response = make_query(query)

    histograms = []
    for res in response["data"]["getHistograms"]:
        histograms.append(int(res["id"]))
    return histograms


def createHistogram(id, xrange, yrange, data=None, name=None, type=None, isLive=False):
    '''
    Create a histogram in the database

    returns: response
    '''
    replacements = {'$ID': id, '$DATA': data, '$XRANGE': xrange, '$YRANGE': yrange, '$NAME': name, '$TYPE': type, '$ISLIVE': isLive}
    query = """mutation create{
                createHistogram( 
                        hist:{
                            id:$ID, 
                            data:$DATA,
                            xrange:$XRANGE,
                            yrange:$YRANGE, 
                            isLive:$ISLIVE, 
                            type: $TYPE,
                            name: $NAME
                        } ) 
                {
                    message
                    success
                }
                }"""
    query = make_replacements(query, replacements)
    return make_query(query)


def getHistogram(id):
    '''
    Get the information from a histogram in the database

    returns: response
    '''
    replacements = {'$ID': id}
    query = """query getHistogram{
                getHistogram(id: $ID){
                        id
                        data{
                            x
                            y
                        }
                        xrange{
                            min
                            max
                        }
                        yrange{
                            min
                            max
                        }    
                        name               
                        type
                        len
                        created
                    }
                }"""
    query = make_replacements(query, replacements)
    return make_query(query)


def getHistograms(ids=None, names=None, minDate=None, maxDate=None, types=None, isLive=False):
    '''
    Retrieve multiple histograms according to filters
    '''
    replacements = {'$IDS': ids, '$NAMES': names, "$MINDATE": minDate, "$MAXDATE": maxDate, "$TYPES": types, "$ISLIVE": isLive}
    query = """query getHistograms{
                        getHistograms( 
                            ids: $IDS
                            names: $NAMES
                            minDate: $MINDATE,
                            maxDate: $MAXDATE,
                            types: $TYPES,
                            isLive: $ISLIVE,
                            )
                            {
                                id
                                name
                                len
                                data {
                                    x
                                    y
                                }
                                xrange {
                                    min
                                    max
                                }
                                yrange {
                                    min
                                    max
                                }
                                type
                                created
                            }
                        }"""
    query = make_replacements(query, replacements)
    return make_query(query)


def updateHistogram(id, data=None, type=None, xrange=None, yrange=None, isLive=False):
    '''
    Updates a histogram in the database

    returns: response
    '''
    replacements = {'$ID': id, '$DATA': data, '$XRANGE': xrange, '$YRANGE': yrange, '$TYPE': type, '$ISLIVE': isLive}
    query = """mutation update{
                updateHistogram( 
                        hist:{
                            id:$ID, 
                            data:$DATA,
                            xrange:$XRANGE,
                            yrange:$YRANGE, 
                            isLive:$ISLIVE, 
                            type: $TYPE,
                        } ) 
                {
                    message
                    success
                }
            }"""
    query = make_replacements(query, replacements)
    return make_query(query)


def deleteHistogram(id, isLive=False):
    '''
    deletes a histogram from the database

    returns: response
    '''
    replacements = {'$ID': id, '$ISLIVE': isLive}
    query = """mutation delete{
                    deleteHistogram(id: $ID, isLive: $ISLIVE)
                    {
                        message
                        success
                    }
                }"""
    query = make_replacements(query, replacements)
    return make_query(query)


def getHistTable(first, after=None):
    '''
    Gets paginated list of runs
    '''
    replacements = {'$FIRST': first, '$AFTER': after}
    query = """query getTable {
                    getHistTableEntries(first:$FIRST, after:$AFTER)
                    {
                        edges{
                            cursor
                            node{
                                name
                                created
                                histIDs
                            }
                        }
                        pageInfo{
                            endCursor
                            hasNextPage
                        }
                    }
                }"""
    query = make_replacements(query, replacements)
    return make_query(query)
