#!/usr/bin/env python3

import argparse

from cachesimulator.simulator import Simulator


# Parse command-line arguments passed to the program
def parse_cli_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--cache-size',
        type=int,
        required=True,
        help='the size of the cache in words')

    parser.add_argument(
        '--num-blocks-per-set',
        type=int,
        default=1,
        help='the number of blocks per set')

    parser.add_argument(
        '--num-words-per-block',
        type=int,
        default=1,
        help='the number of words per block')

    parser.add_argument(
        '--word-addrs',
        nargs='+',
        type=int,
        required=True,
        help='one or more base-10 word addresses')

    parser.add_argument(
        '--num-addr-bits',
        type=int,
        default=1,
        help='the number of bits in each given word address')

    parser.add_argument(
        '--replacement-policy',
        choices=('lru', 'mru'),
        default='lru',
        # Ignore argument case (e.g. "mru" and "MRU" are equivalent)
        type=str.lower,
        help='the cache replacement policy (LRU or MRU)')

    return parser.parse_args()


def main():

    cli_args = parse_cli_args()
    sim = Simulator()
    sim.run_simulation(**vars(cli_args))


if __name__ == '__main__':
    main()
