#!/usr/bin/env python2
"""Command line arguments handling."""

import optparse

parser = optparse.OptionParser()

parser.add_option("-s", "--scenario", help="play only the following "+
                  "scenario, omitting the main menu", action="store",
                  dest="scenario")
parser.add_option("-q", "--quiet", help="don't print anything",
                  action="store_true", default=False, dest="quiet")
parser.add_option("--version", help="print version number and quit",
                  action="store_true", default=False, dest="print_version")

options, args = parser.parse_args()


# Test
if __name__ == "__main__":
    print options, args
