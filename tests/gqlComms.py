from os import replace
import sys
from webbrowser import get
import requests 
import json

ENDPOINT = 'http://127.0.0.1:8000/graphql/'

def print_response(response):
    print(json.dumps(response, indent=2))

def make_replacements(string, replacements):
    for key, value in replacements.items():
        string = string.replace(key, str(value))
    return string

def check_response_errors(response):
    error = response.get("errors")
    if error is not None:
        print_response(error)
        sys.exit()

def make_query(query, url=ENDPOINT, headers=None):
    request = requests.post(url, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def listHistograms(isLive='false'):
    '''kwargs get directly converted to strings'''
    replacements = {'$ISLIVE': isLive}
    query = """query list{
                listHistograms(isLive:$ISLIVE)
            }"""
    query = make_replacements(query, replacements)
    response = make_query(query)
    histograms = []
    try:
        for id in response["data"]["listHistograms"]:
            histograms.append(int(id))
    except Exception as e:
        print_response(response)
        print(e)
        sys.exit()

    check_response_errors(response)
    return histograms, response

def createHistogram(id, x, y, name, type, isLive):
    '''kwargs get directly converted to strings'''
    replacements = {'$ID':id, '$XDATA':x, '$YDATA':y,
                    '$NAME': name, '$TYPE': type, '$ISLIVE': isLive}
    query = """mutation create{
                createHistogram( 
                        hist:{
                            id:$ID, 
                            x:$XDATA, 
                            y:$YDATA,
                            isLive:$ISLIVE, 
                            type: "$TYPE",
                            name: "$NAME"
                        } ) 
                {
                    message
                    success
                }
                }"""
    query = make_replacements(query, replacements)
    response = make_query(query)
    check_response_errors(response)
    return response

def updateHistogram(id, x, y, name, type, isLive):
    '''kwargs get directly converted to strings'''
    replacements = {'$ID':id, '$XDATA':x, '$YDATA':y,
                    '$NAME': name, '$TYPE': type, '$ISLIVE': isLive}
    query = """mutation update{
                updateHistogram( 
                        hist:{
                            id:$ID, 
                            x:$XDATA, 
                            y:$YDATA,
                            isLive:$ISLIVE, 
                            type:"$TYPE",
                            name: "$NAME"
                        } ) 
                {
                    message
                    success
                }
            }"""
    query = make_replacements(query, replacements)
    response = make_query(query)
    check_response_errors(response)

def deleteHistogram(id, isLive):
    '''kwargs get directly converted to strings'''
    replacements = {'$ID':id, '$ISLIVE': isLive}
    query = """mutation delete{
                    deleteHistogram(id: $ID, isLive: $ISLIVE)
                    {
                        message
                        success
                    }
                }"""
    query = make_replacements(query, replacements)
    response = make_query(query)
    check_response_errors(response)
    return response