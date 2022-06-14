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

### Subscriptions ###
LIVE_HIST_SUBSCRIPTION = """subscription histSub {
                                getLiveHistograms {
                                    histograms{
                                    id
                                    name
                                    created
                                    type
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
                                    current {
                                        x
                                        y
                                    }
                                    }
                                    lastRun  
                                }
                                }"""
