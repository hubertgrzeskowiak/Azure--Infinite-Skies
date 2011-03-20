"""Command line arguments handling."""

import sys
import optparse

# constants for -v,-d and -q options are found in errors module
from errors import *

parser = optparse.OptionParser()

parser.add_option("-s", "--scenario", help="start with the following "+
                  "scenario, omitting the main menu", action="store",
                  dest="scenario")
parser.add_option("-q", "--quiet", help="don't print anything",
                  action="store_true", default=False, dest="quiet")
parser.add_option("--version", help="print version number and quit",
                  action="store_true", default=False, dest="print_version")

options, args = parser.parse_args()
#setErrAction(options.verbose)


# Test
if __name__ == "__main__":
    print options, args
