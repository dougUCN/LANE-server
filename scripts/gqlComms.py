"""
Functions for communication with graphql endpoint via python
"""
import requests
import json
import numpy as np
import datetime

### Constants ###

ENDPOINT = 'http://127.0.0.1:8000/graphql/'


def dump_response(response):
    '''Dump a json response to str with indent 2'''
    return json.dumps(response, indent=2)


def check_response(response):
    '''
    Check for the existence of errors in the graphql response json
    '''
    error = response.json().get("errors")
    if error is not None:
        raise RuntimeError(dump_response(error))
    if response.status_code != 200:
        raise RuntimeError(f'Query failed to run by returning code of {response.status_code}')
    return response


def toSvgCoords(xList, yList):
    '''
    Takes two lists x and y and creates a dictionary
    [{"x": x0, "y": y0},
    {"x": x1, "y": y1},
    ...]
    '''
    return [{'x': x, 'y': y} for (x, y) in zip(xList, yList)]


def listHistograms(ids=None, names=None, minDate=None, maxDate=None, types=None, isLive=False):
    '''
    Returns a list of all histograms in the database

    returns: list of histogram IDs in the database
    '''
    response = requests.post(
        ENDPOINT,
        json={"query": GET_HIST_IDS, "variables": locals()},
    )
    check_response(response)
    data = response.json()["data"]["getHistograms"]
    histogramList = []
    for datum in data:
        histogramList.append(int(datum['id']))
    return histogramList


def createHistogram(id, xrange=None, yrange=None, data=None, name=None, type=None, isLive=False):
    '''
    Create a histogram in the database

    returns: response json
    '''
    response = requests.post(
        ENDPOINT,
        json={
            "query": CREATE_HIST,
            "variables": {"hist": locals()},
        },
    )
    check_response(response)
    return response.json()


def getHistogram(id, isLive=False):
    '''
    Get the information from a histogram in the database

    returns: response json
    '''
    response = requests.post(
        ENDPOINT,
        json={"query": GET_HISTOGRAM, "variables": locals()},
    )
    check_response(response)
    return response.json()


def getHistograms(ids=None, names=None, minDate=None, maxDate=None, types=None, isLive=False):
    '''
    Retrieve multiple histograms according to filters

    returns: response json
    '''
    response = requests.post(
        ENDPOINT,
        json={
            "query": GET_HISTOGRAMS,
            "variables": locals(),
        },
    )
    check_response(response)
    return response.json()


def updateHistogram(id, data=None, type=None, xrange=None, yrange=None, isLive=False):
    '''
    Updates a histogram in the database

    returns: response json
    '''
    response = requests.post(
        ENDPOINT,
        json={
            "query": UPDATE_HIST,
            "variables": {"hist": locals()},
        },
    )
    check_response(response)
    return response.json()


def deleteHistogram(id, isLive=False):
    '''
    deletes a histogram from the database

    returns: response json
    '''
    response = requests.post(
        ENDPOINT,
        json={
            "query": DELETE_HIST,
            "variables": locals(),
        },
    )
    check_response(response)
    return response.json()


def getHistTable(first, after=None):
    '''
    Gets paginated list of runs
    '''
    response = requests.post(
        ENDPOINT,
        json={"query": GET_HIST_TABLE, "variables": locals()},
    )
    check_response(response)
    return response.json()


### Queries ###

GET_HIST_TABLE = """query getHistTable($first: Int!, $after: String) {
                    getHistTableEntries(first: $first, after: $after)
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

GET_HIST_IDS = """query getIDs( $ids: [ID], 
                            $names: [String],
                            $minDate: Datetime,
                            $maxDate: Datetime,
                            $types: [String],
                            $isLive: Boolean,
                        )
                    {
                    getHistograms( 
                            ids: $ids,
                            names: $names,
                            minDate: $minDate,
                            maxDate: $maxDate,
                            types: $types,
                            isLive: $isLive
                            )
                        {
                            id
                        }
                    }"""

GET_HISTOGRAM = """query getHistogram( $id: ID!, $isLive: Boolean)
                    {
                    getHistogram( id: $id, isLive: $isLive)
                        {
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

GET_HISTOGRAMS = """query getIDs( $ids: [ID], 
                            $names: [String],
                            $minDate: Datetime,
                            $maxDate: Datetime,
                            $types: [String],
                            $isLive: Boolean,
                        )
                    {
                    getHistograms( 
                            ids: $ids,
                            names: $names,
                            minDate: $minDate,
                            maxDate: $maxDate,
                            types: $types,
                            isLive: $isLive
                            )
                        {
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


### Mutations ###

CREATE_HIST = """mutation create($hist: HistogramInput!){
                    createHistogram( hist: $hist ) 
                    {
                        message
                        success
                    }
                }"""

DELETE_HIST = """mutation delete($id: ID!, $isLive: Boolean){
                    deleteHistogram(id: $id, isLive: $isLive)
                    {
                        message
                        success
                    }
                }"""

UPDATE_HIST = """mutation update($hist: HistogramUpdateInput!){
                    updateHistogram( hist: $hist ) 
                    {
                        message
                        success
                    }
                }"""
