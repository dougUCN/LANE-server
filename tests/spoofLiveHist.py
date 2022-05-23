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

import datetime, time, argparse
from tkinter import Y
from gqlComms import listHistograms, createHistogram, deleteHistogram, updateHistogram
import numpy as np

NUMALIVE = 4
LIVETIME = 20
PAUSE = 5
NCYCLES = 1
LOW = 0
HIGH = 1000


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-na',
        '--numAlive',
        type=int,
        default=NUMALIVE,
        help=f'Max number of live histograms at a given moment (default={NUMALIVE})',
    )
    parser.add_argument('-lw', '--low', type=int, default=LOW, help=f'Smallest possible integer value in a histogram (default={LOW})')
    parser.add_argument('-hi', '--high', type=int, default=HIGH, help=f'Largest possible integer value in a histogram (default={HIGH})')
    parser.add_argument(
        '-lt',
        '--liveTime',
        type=int,
        default=LIVETIME,
        help=f'Seconds histograms stay live before they are removed (default={LIVETIME})',
    )
    parser.add_argument('-p', '--pause', type=int, default=PAUSE, help=f'Seconds to pause between cycles (default={PAUSE})')
    parser.add_argument(
        '-n',
        '--nCycles',
        type=int,
        default=NCYCLES,
        help=f'Number of cycles for which this test is repeated (default={NCYCLES})',
    )
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    currentHists, response = listHistograms(isLive=True)
    histsToMake = np.arange(args.numAlive)
    overlap = list(set(histsToMake) & set(currentHists))

    if overlap and not args.force:
        raise Exception(
            """WARNING: There currently exist histograms in the live database!
Run with the --force flag to force an overwrite!"""
        )

    elif overlap and args.force:
        print(f"Deleting histograms {overlap}")
        for id in overlap:
            deleteHistogram(id, isLive=True)
        print(f"Delete completed")

    now = datetime.datetime.now()
    runHeader = now.strftime("%Y%m%d_run")

    # PRNG
    rng = np.random.default_rng()

    for cycle in range(args.nCycles):
        print(f'Cycle {cycle + 1}/{args.nCycles}')
        # Inialize live histograms
        print('Initializing empty live histograms')
        for id in histsToMake:
            params = {
                'id': id,
                'name': f'{runHeader}{id}',
                'type': 'live_test',
                'isLive': True,
            }
            createHistogram(**params)

        print('Live updating histograms')
        data = '['
        FIRST = True
        for t in range(args.liveTime):
            for id in histsToMake:
                y = rng.integers(low=args.low, high=args.high)

                if FIRST:
                    yMin = y
                    yMax = y
                    FIRST = False
                else:
                    if y < yMin:
                        yMin = y
                    if y > yMax:
                        yMax = y

                data = data + f'{{x:{t},y:{y}}},'

                params = {
                    'id': id,
                    'data': data + ']',
                    'xrange': {'min': 0, 'max': t},
                    'yrange': {'min': yMin, 'max': yMax},
                    'isLive': True,
                }
                updateHistogram(**params)
            time.sleep(1)

        print('LiveTime complete. Pausing')
        time.sleep(args.pause)

        # Cleanup the live histograms you created at the end of each cycle
        print('Cleaning up live histograms')
        for id in histsToMake:
            deleteHistogram(id, isLive=True)
        currentHists, response = listHistograms(isLive=True)
        print(f'Current histograms in database: {currentHists}')

    print('Done')


if __name__ == "__main__":
    main()
