#!/usr/bin/env python
"""
Fills the static database with fake histograms
containing random x y data

Make sure the BE is running before starting this script

For testing options run `python spoofStaticHist.py --help`

If database is not empty, appends new histograms
"""

from gqlComms import createHistogram, getHistTable, toSvgCoords
import numpy as np
import argparse

NUM = 100
LENGTH = 50
LOW = 0
HIGH = 1000
PER = 4


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n', '--num', type=int, default=NUM, help=f'Add this many runs to the database (default={NUM})')
    parser.add_argument('-p', '--per', type=int, default=PER, help=f'Add this many histograms per run (default={PER})')
    parser.add_argument('-l', '--length', type=int, default=LENGTH, help=f'Number of datapoints per histogram (default={LENGTH})')
    parser.add_argument('-lw', '--low', type=int, default=LOW, help=f'Smallest possible integer value in a histogram (default={LOW})')
    parser.add_argument('-hi', '--high', type=int, default=HIGH, help=f'Largest possible integer value in a histogram (default={HIGH})')
    args = parser.parse_args()

    runHeader = 'run'

    # PRNG
    rng = np.random.default_rng()
    x = np.arange(args.length).tolist()

    # Check existing histograms in db
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

    # Create histograms
    print('Creating histograms')
    hist_id = int(hist_offset)
    for run_id in np.arange(run_offset, run_offset + args.num):
        for type_id in np.arange(args.per):
            y = rng.integers(low=args.low, high=args.high, size=args.length).tolist()
            params = {
                'id': hist_id,
                'data': toSvgCoords(x, y),
                'xrange': {'min': x[0], 'max': x[-1]},
                'yrange': {'min': args.low, 'max': args.high},
                'name': f'{runHeader}{run_id}',
                'type': f'detector_type_{type_id}',
                'isLive': False,
            }
            createHistogram(**params)
            hist_id += 1


if __name__ == "__main__":
    main()
