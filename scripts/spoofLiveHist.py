#!/usr/bin/env python
"""
Automatically creates and removes live histograms for testing
the histogram subscription graphql api

Make sure the BE is running before starting this script

[numAlive] histograms are added to the database, where they persist 
for [liveTime] seconds before being removed. The test script then 
pauses for [pause] seconds before repeating the cycle [nCycles] times

For testing options run `python spoofLiveHist.py --help`
"""

import time, argparse
from gqlComms import (
    listHistograms,
    createHistogram,
    deleteHistogram,
    updateHistogram,
    getHistTable,
)
import numpy as np

NUMALIVE = 4
LIVETIME = 20
PAUSE = 5
NCYCLES = 1
LOW = 0
HIGH = 1000


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-na', '--numAlive', type=int, default=NUMALIVE, help=f'Max number of live histograms at a given moment (default={NUMALIVE})')
    parser.add_argument('-lw', '--low', type=int, default=LOW, help=f'Smallest possible integer value in a histogram (default={LOW})')
    parser.add_argument('-hi', '--high', type=int, default=HIGH, help=f'Largest possible integer value in a histogram (default={HIGH})')
    parser.add_argument('-lt', '--liveTime', type=int, default=LIVETIME, help=f'Seconds histograms stay live before they are removed (default={LIVETIME})')
    parser.add_argument('-p', '--pause', type=int, default=PAUSE, help=f'Seconds to pause between cycles (default={PAUSE})')
    parser.add_argument('-n', '--nCycles', type=int, default=NCYCLES, help=f'Number of cycles for which this test is repeated (default={NCYCLES})')
    args = parser.parse_args()

    # Check existing histograms in db and create new histID + runID

    runHeader = 'run'

    print('Checking database for existing histograms')
    data = getHistTable(first=1)['data']['getHistTableEntries']
    if not data['edges']:
        hist_offset = 0
        run_offset = 0
    else:
        hist_offset = np.amax([int(id) for id in data['edges'][0]['node']['histIDs']]) + 1

        if runHeader in data['edges'][0]['node']['name']:
            run_offset = int(data['edges'][0]['node']['name'].split(runHeader)[1]) + 1
        else:
            run_offset = 0

    rng = np.random.default_rng()
    histsToMake = np.arange(hist_offset, hist_offset + args.numAlive).tolist()
    run_id = run_offset
    initial_data = {id: [] for id in histsToMake}
    xlimit = {id: 10 for id in histsToMake}

    for cycle in range(args.nCycles):
        print(f'Cycle {cycle + 1}/{args.nCycles}')
        # Inialize live histograms
        print('Initializing empty live histograms')
        for id in histsToMake:
            params = {
                'id': id,
                'name': f'{runHeader}{run_id}',
                'type': f'detector{id}',
                'xrange': {'min': 0, 'max': 10},
                'yrange': {'min': args.low, 'max': args.high},
                'isLive': True,
            }
            createHistogram(**params)

        print('Live updating histograms')
        data = initial_data
        for t in range(args.liveTime):
            for id in histsToMake:
                data[id].append({'x': t, 'y': int(rng.integers(low=args.low, high=args.high))})
                params = {
                    'id': id,
                    'data': data[id],
                    'isLive': True,
                }

                # Expand x axis range by 10 every time x axis limit is exceeded
                if t > xlimit[id]:
                    xlimit[id] += 10
                    params['xrange'] = {'min': 0, 'max': xlimit[id]}

                updateHistogram(**params)
            time.sleep(1)

        print('LiveTime complete. Pausing')
        time.sleep(args.pause)

        # Cleanup the live histograms you created at the end of each cycle
        print('Cleaning up live histograms')
        for id in histsToMake:
            deleteHistogram(id, isLive=True)
        currentHists = listHistograms(isLive=True)
        print(f'Current histograms in database: {currentHists}')

    print('Done')


if __name__ == "__main__":
    main()
