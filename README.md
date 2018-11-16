# bingraph
Utility(ies?) for helping to manage the relationships between sets of binaries and their libraries

Dependencies:
-------------
pyelftools (https://github.com/eliben/pyelftools)


Usage:
------
./bingraph.py libs_dir exec_file


Notes:
------
This tool emulates a portion of the runtime linux ELF linker in order to resolve symbols in the ELF segments.  This allows you to see which exported symbols in a library are actually being called by the binary file. That doesn't seem very valuable, but if you're looking at a library which is exporting a lot of things, understanding where execution starts is a good starting place.

Eventually, I hope to turn this into a visual tool graphing relations in sort of a UML diagram format.

Thanks Department 13 for letting me publish this.
