#!/usr/bin/env python
"""
Fills the static database with fake histograms
containing random x y data

Make sure the BE is running before starting this script

For testing options run `python spoofStaticHist.py --help`
"""
import datetime
from gqlComms import listHistograms, createHistogram, deleteHistogram
import numpy as np
import argparse
import sys


NUM = 100
LENGTH = 50
LOW = 0
HIGH = 1000


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        '-o',
        '--offset',
        type=int,
        default=0,
        help='Start creating histogram with ids starting from this integer (default=0)',
    )
    parser.add_argument('-n', '--num', type=int, default=NUM, help=f'Add this many histograms to the database (default={NUM})')
    parser.add_argument('-l', '--length', type=int, default=LENGTH, help=f'Number of datapoints per histogram (default={LENGTH})')
    parser.add_argument('-lw', '--low', type=int, default=LOW, help=f'Smallest possible integer value in a histogram (default={LOW})')
    parser.add_argument('-hi', '--high', type=int, default=HIGH, help=f'Largest possible integer value in a histogram (default={HIGH})')
    parser.add_argument('--delete', action='store_true', help='Deletes the histograms instead of creating (if they exist)')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    currentHists, response = listHistograms(isLive=False)
    num = np.arange(args.offset, args.num + args.offset)
    overlap = list(set(num) & set(currentHists))

    if args.delete and not args.force:
        raise Exception(
            f"""WARNING: You are about to delete histograms with IDs from {num[0]} to {num[-1]}
Run with the --force flag to continue"""
        )
    elif args.delete and args.force:
        for id in overlap:
            deleteHistogram(id, isLive=False)
        currentHists, response = listHistograms(isLive=False)
        print(f'Current histograms in database: {currentHists}')
        sys.exit()

    if currentHists and not args.force:
        raise Exception(
            """WARNING: There currently exist histograms in the static database!
This script will not overwrite existing histograms.
Run with the --force flag to continue."""
        )

    # Safeguards to make sure existing histograms are not written over
    if overlap:
        print(f"Existing histograms of id:{overlap} will not be overwritten")

    histsToMake = [x for x in num if x not in overlap]
    now = datetime.datetime.now()
    runHeader = now.strftime("%Y%m%d_run")

    # PRNG
    rng = np.random.default_rng()

    # Create histograms
    print('Creating histograms')
    for id in histsToMake:
        params = {
            'id': id,
            'x': np.arange(args.length).tolist(),
            'y': rng.integers(low=args.low, high=args.high, size=args.length).tolist(),
            'name': f'{runHeader}{id}',
            'type': 'static_test',
            'isLive': False,
        }
        createHistogram(**params)

    # Check histograms inserted in database
    currentHists, response = listHistograms(isLive=False)
    print(f'Current histograms in database: {currentHists}')


if __name__ == "__main__":
    main()
