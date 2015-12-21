# Cache Simulator

*Copyright 2015 Caleb Evans*  
*Released under the MIT license*

This program simulates a processor cache for the MIPS instruction set architecture. It can simulate all three fundamental caching schemes: direct-mapped, *n*-way set associative, and fully associative.

The program must be run from the command line and requires Python 3 to run. Executing the program will run the simulation and print an ASCII table containing the details for each supplied word address, as well as the final contents of the cache.

To see example input and output, see `examples.txt`.

## Command-line parameters

### Required parameters

#### --cache-size

The size of the cache in words (recall that one word is four bytes in MIPS).

#### --num-blocks-per-set

The program internally represents all cache schemes using a set associative cache. A value of `1` for this parameter implies a direct-mapped cache. A value other than `1` implies either a set associative or fully associative cache.

#### --num-words-per-block

The number of words to store for each block in the cache.

#### --word-addrs

One or base-10 word addresses, separated by spaces.

### Optional parameters

#### --num-addr-bits

The number of bits used to represent each given word address; this value is reflected in the *BinAddr* column in the address table. If omitted, the default value is the number of bits needed to represent the largest word address.

#### --replacement-policy

The replacement policy to use for the cache. Accepted values are `lru` (Least Recently Used) and `mru` (Most Recently Used). The default value is `lru`.
