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
from gqlComms import listHistograms, createHistogram, deleteHistogram, updateHistogram
import numpy as np

NUMALIVE = 4
LIVETIME = 20
PAUSE = 5
NCYCLES = 2
LOW = 0
HIGH =1000

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-na','--numAlive', type=int, default=NUMALIVE, 
                        help=f'Max number of live histograms at a given moment (default={NUMALIVE})')
    parser.add_argument('-lw','--low', type=int, default=LOW, 
                    help=f'Smallest possible integer value in a histogram (default={LOW})')
    parser.add_argument('-hi','--high', type=int, default=HIGH, 
                    help=f'Largest possible integer value in a histogram (default={HIGH})')
    parser.add_argument('-lt','--liveTime', type=int, default=LIVETIME, 
                    help=f'Seconds histograms stay live before they are removed (default={LIVETIME})')
    parser.add_argument('-p', '--pause', type=int, default=PAUSE,
                    help=f'Seconds to pause between cycles (default={PAUSE})')
    parser.add_argument('-n', '--nCycles', type=int, default=NCYCLES,
                    help=f'Number of cycles for which this test is repeated (default={NCYCLES})')
    parser.add_argument('--force', action='store_true', help='Overwrite any existing entries in the database')
    args = parser.parse_args()

    
    currentHists, response = listHistograms(isLive='true')
    numAlive = np.arange(args.numAlive)
    overlap = list(set(numAlive) & set(currentHists))
    
    if currentHists and not args.force:
        raise Exception("""WARNING: There currently exist histograms in the live database!
This script will not overwrite existing histograms.
Run with the --force flag to continue.""")

    # Safeguards to make sure existing histograms are not written over
    if overlap:
        print(f"Existing histograms of id:{overlap} will not be overwritten")

    histsToMake = [x for x in numAlive if x not in overlap]
    

    now = datetime.datetime.now()
    runHeader = now.strftime("%Y%m%d_run")
    
    
    # PRNG
    rng = np.random.default_rng()

   
    for cycle in range(args.nCycles):
        print(f'Cycle {cycle + 1}/{args.nCycles}')
        # Inialize live histograms
        print('Initializing empty live histograms')
        for id in histsToMake:
            params ={
                'id': id,
                'x': 'null',
                'y': 'null', 
                'name': f'{runHeader}{id}', 
                'type': 'live_test', 
                'isLive': 'true',
            }
            createHistogram( **params )

        print('Live updating histograms')
        yData = {new_list: [] for new_list in histsToMake}
        xData = {new_list: [] for new_list in histsToMake}
        for t in range(args.liveTime):
            for id in histsToMake:
                xData[id].append( t )
                yData[id].append( rng.integers(low=args.low, high=args.high) )
                params ={
                    'id': id,
                    'x': xData[id],
                    'y': yData[id], 
                    'name': 'null', 
                    'type': 'null', 
                    'isLive': 'true',
                }
                updateHistogram(**params)
            time.sleep(1)

        print('LiveTime complete. Pausing')
        time.sleep(args.pause)

        # Cleanup the live histograms you created at the end of each cycle
        print('Cleaning up live histograms')
        for id in histsToMake:
            deleteHistogram(id, isLive='true')
        currentHists, response = listHistograms(isLive='true')
        print(f'Current histograms in database: {currentHists}')
    
    print('Done')
    

if __name__ == "__main__":
    main()