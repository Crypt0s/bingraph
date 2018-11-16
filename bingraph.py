#!/usr/bin/python
#
#   bingraph.py
#
#   bingraph.py is a utility to emulate a slice of the dynamic linker functionality -- the discovery and resolution of
#   dynamically-loaded symbols.  This is useful because you may wish to know which shared object files are providing
#   which functions to an executable at runtime in order to focus reverse engineering only on the parts of the .so file
#   that are being run by the executable, or to quickly understand which functions are "entry" points to the library.
#
#
from elftools.elf.elffile import ELFFile
import sys

def get_info(filename):
    imported_symbols = []
    imported_libs = []
    implemented_symbols = []

    #elftools requires fp type - open and pass
    file = open(filename)

    # process the filepointer with the ELFTools package
    elffile = ELFFile(file)

    # we need two segements -- what symbols we have in this ELF (.dynsym) and what libraries this ELF depends on during
    # the linking stage (.dynamic).  We will examine each section in order to determine where imports are located.
    dynsym = elffile.get_section_by_name('.dynsym')
    dynamic = elffile.get_section_by_name('.dynamic')

    # .dynsym segment contains symbols defined inside the ELF file.
    # these symbols aren't necessarily implemented in this file -- you can find out which are by looking at the location
    # of the segment in which the symbol is defined.  If no segment location is present (SHN_UNDEF) then it's imported
    # otherwise, it's implemented and located inside /this/ ELF.  We will look at resolution of this symbol later.
    for i in range(0,dynsym.num_symbols()):
        symbol = dynsym.get_symbol(i)
        if symbol.entry['st_shndx'] == 'SHN_UNDEF':
            #print "imported symbol: %s" % symbol.name
            imported_symbols.append(symbol.name)
        else:
            #print "implemented symbol: %s" % symbol.name
            implemented_symbols.append(symbol.name)

    # now that we know which symbols we need to resolve, we will need to look at hints for resolution.  The linker is
    # told by the ELF about which libraries are required in order to execute code.  We will utilize those files and
    # attempt to find undefined symbols from .dynsym segment in these files.  To do that we process only what those
    # files report as being implemented in their ELF .dynsym segments.

    #TODO: make this recursive -- if a processed dependency has a DT_NEEDED segment we should note that too
    for i in range(0,dynamic.num_tags()):
        try:
            entry = dynamic.get_tag(i)
            if 'DT_NEEDED' in entry.entry.values():
                imported_libs.append(entry.needed)
        except Exception,e:
                print str(e)

    return (imported_libs, imported_symbols, implemented_symbols)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage:"
        print "./bingraph.py libs_dir exec_file"
        exit()

    lib_path = sys.argv[1]
    file_path = sys.argv[2]
    imported_libs, imported_symbols, implemented_symbols = get_info(file_path)

    # clean up some user args for convenience of the user.
    if lib_path[-1] != "/":
        lib_path = lib_path+"/"

    # once we have the libraries and symbols we need to resolve, start iterating thru them to find out which has what
    for i in imported_libs:
        #print "import: %s" % i
        try:
            (dontcare, dontcare2, lib_implemented_symbols) = get_info("%s%s" % (lib_path, i))

        # handle a case where there wasn't a library present.
        except IOError, e:
            print "No such library present in lib directory"
            print e
            continue

        print "////////////////////////////////////////////////////////////"
        print "%s implements" % i
        # this intersection prints only those symbols which are imported from the analyzed bin and marked as implemented
        # in the analyzed imported library's .dynsym segment.
        for z in set(lib_implemented_symbols).intersection(set(imported_symbols)):
            print "---- %s" % z
        print "////////////////////////////////////////////////////////////"

