# Cache Simulator

*Copyright 2015-2024 Caleb Evans*  
*Released under the MIT license*

[![tests](https://github.com/caleb531/cache-simulator/actions/workflows/tests.yml/badge.svg)](https://github.com/caleb531/cache-simulator/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/caleb531/cache-simulator/badge.svg)](https://coveralls.io/r/caleb531/cache-simulator?branch=main)

This program simulates a processor cache for the MIPS instruction set
architecture. It can simulate all three fundamental caching schemes:
direct-mapped, *n*-way set associative, and fully associative.

The program must be run from the command line and requires Python 3.4+ to run.
Executing the program will run the simulation and print an ASCII table
containing the details for each supplied word address, as well as the final
contents of the cache.

For example, the following command simulates a 3-way set associative LRU cache,
with 2 words per block. To see all examples and their respective outputs, see
[examples.txt](examples.txt).

```sh
# 3-way set associative (LRU; 2 words per block)
cache-simulator --cache-size 24 --num-blocks-per-set 3 --num-words-per-block 2 --word-addrs 3 180 43 2 191 88 190 14 181 44 186 253
```

This produces the following output:

```
     WordAddr      BinAddr          Tag        Index       Offset     Hit/Miss
--------------------------------------------------------------------------------
            3    0000 0011        00000           01            1         miss
          180    1011 0100        10110           10            0         miss
           43    0010 1011        00101           01            1         miss
            2    0000 0010        00000           01            0          HIT
          191    1011 1111        10111           11            1         miss
           88    0101 1000        01011           00            0         miss
          190    1011 1110        10111           11            0          HIT
           14    0000 1110        00001           11            0         miss
          181    1011 0101        10110           10            1          HIT
           44    0010 1100        00101           10            0         miss
          186    1011 1010        10111           01            0         miss
          253    1111 1101        11111           10            1         miss

                                     Cache
--------------------------------------------------------------------------------
         00                  01                  10                  11
--------------------------------------------------------------------------------
       88,89         2,3 42,43 186,187  180,181 44,45 252,253   190,191 14,15
```

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
