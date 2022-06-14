"""
Queries, Mutations, Subscriptions and additional functions used for unit tests
"""

### Common Functions ###


def toSvgCoords(xList, yList):
    '''
    Takes two lists x and y and creates a dictionary
    [{"x": x0, "y": y0},
    {"x": x1, "y": y1},
    ...]
    '''
    return [{'x': x, 'y': y} for (x, y) in zip(xList, yList)]


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
