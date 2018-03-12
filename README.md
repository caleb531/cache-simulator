# Cache Simulator

*Copyright 2015-2018 Caleb Evans*  
*Released under the MIT license*

[![Build Status](https://travis-ci.org/caleb531/cache-simulator.svg?branch=master)](https://travis-ci.org/caleb531/cache-simulator)
[![Coverage Status](https://coveralls.io/repos/caleb531/cache-simulator/badge.svg?branch=master)](https://coveralls.io/r/caleb531/cache-simulator?branch=master)

This program simulates a processor cache for the MIPS instruction set
architecture. It can simulate all three fundamental caching schemes:
direct-mapped, *n*-way set associative, and fully associative.

The program must be run from the command line and requires Python 3.4+ to run.
Executing the program will run the simulation and print an ASCII table
containing the details for each supplied word address, as well as the final
contents of the cache.

To see example input and output, see `examples.txt`.

## Installing

You can install Cache Simulator via pip (ideally globally):

```
pip install cache-simulator
```

## Command-line parameters

### Required parameters

#### --cache-size

The size of the cache in words (recall that one word is four bytes in MIPS).

#### --word-addrs

One or more word addresses (separated by spaces), where each word address is a
base-10 positive integer.

### Optional parameters

#### --num-blocks-per-set

The program internally represents all cache schemes using a set associative
cache. A value of `1` for this parameter (the default) implies a direct-mapped
cache. A value other than `1` implies either a set associative *or* fully
associative cache.

#### --num-words-per-block

The number of words to store for each block in the cache; the default value is `1`.

#### --num-addr-bits

The number of bits used to represent each given word address; this value is
reflected in the *BinAddr* column in the reference table. If omitted, the
default value is the number of bits needed to represent the largest of the given
word addresses.

#### --replacement-policy

The replacement policy to use for the cache. Accepted values are `lru` (Least
Recently Used; the default) and `mru` (Most Recently Used).
