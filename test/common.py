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

GET_HIST_TABLE = """
query getHistTable($first: Int!, $after: String) {
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

GET_HIST_IDS = """
query getIDs($ids: [ID], 
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

GET_HISTOGRAM = """
query getHistogram($id: ID!, $isLive: Boolean)
{
    getHistogram(id: $id, isLive: $isLive)
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

GET_HISTOGRAMS = """
query getIDs($ids: [ID], 
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

GET_DEVICE = """
query getDevice ($name: String!) {
    getDevice(name: $name){
        name
        isOnline
        deviceOptions{
            optionName
            deviceOptionType
            selected
            options
        }
    }
}"""

GET_DEVICES = """
query getDevices {
    getDevices{
        name
        isOnline
        deviceOptions{
            optionName
            deviceOptionType
            selected
            options
        }
    }
}"""

GET_RUN_CONFIG = """
query getRunConfig($id: ID!){
    getRunConfig (id: $id){
            id
            name
            lastLoaded
            lastSaved
            priority
            runConfigStatus{
                status
                messages
            }
            totalTime
            steps{
                time
                description
                deviceName
                deviceOptions{
                    optionName
                    deviceOptionType
                    selected
                    options
                    }
            }
    }
}"""

GET_RUN_CONFIGS = """
query getRunConfigs {
    getRunConfigs{
        runConfigs{
            id
            name
            lastLoaded
            lastSaved
            priority
            runConfigStatus{
                status
                messages
            }
            totalTime
            steps{
                time
                description
                deviceName
                deviceOptions{
                    optionName
                    deviceOptionType
                    selected
                    options
                }
            }
        }
        canCreateNewRun
    }
}"""

### Mutations ###

CREATE_HIST = """
mutation create($hist: HistogramInput!){
    createHistogram(hist: $hist) 
    {
        message
        success
    }
}"""

DELETE_HIST = """
mutation delete($id: ID!, $isLive: Boolean){
    deleteHistogram(id: $id, isLive: $isLive)
    {
        message
        success
    }
}"""

UPDATE_HIST = """
mutation update($hist: HistogramUpdateInput!){
    updateHistogram( hist: $hist ) 
    {
        message
        success
    }
}"""

CREATE_DEVICE = """mutation createDevice($device: DeviceInput!){
	createDevice(device: $device)
	{
		message
		success
		modifiedDevice{
                name
                isOnline
                deviceOptions{
                    optionName
                    deviceOptionType
                    selected
                    options
                }
        }
	}
}"""

DELETE_DEVICE = """
mutation deleteDevice($name: String!){
	deleteDevice(name: $name)
		{
			message
			success
			modifiedDevice{
				name
			}
		}
}"""

UPDATE_DEVICE = """
mutation updateDevice($device: DeviceInput!){
    updateDevice(device: $device)
    {
        message
        success
        modifiedDevice{
            name
            isOnline
            deviceOptions{
                optionName
                deviceOptionType
                selected
                options
            }
        }
    }
}"""

CREATE_RUN_CONFIG = """
mutation createRunConfig($runConfig: RunConfigInput!){
    createRunConfig(runConfig: $runConfig)
    {
        message
        success
        modifiedRunConfig{
            id
            lastSaved
        }
    }
}"""

DELETE_RUN_CONFIG = """
mutation deleteRunConfig($id: ID!){
	deleteRunConfig(id: $id){
		message
		success
		modifiedRunConfig{
			id
		}
	}
}
"""

UPDATE_RUN_CONFIG = """
mutation updateRunConfig($runConfig: RunConfigUpdateInput!){
	updateRunConfig(runConfig: $runConfig)
	{
		message
		success
		modifiedRunConfig{
            id
            name
            lastLoaded
            lastSaved
            priority
            runConfigStatus{
                status
                messages
            }            
            totalTime
            steps{
                time
                description
                deviceName
                deviceOptions{
                    optionName
                    deviceOptionType
                    selected
                    options
                    }
                }
		}
	}
}
"""

### Subscriptions ###
LIVE_HIST_SUBSCRIPTION = """
subscription histSub {
    getLiveHistograms {
        histograms{
        id
        name
        created
        type
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
        current {
            x
            y
        }
        }
        lastRun  
    }
}"""
