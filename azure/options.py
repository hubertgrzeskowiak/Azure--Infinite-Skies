"""Command line arguments handling."""

import optparse

# constants for -v,-d and -q options are found in errors module
from errors import *

def createOptionParser():
    """Creates a parser object and returns it. To call any options' values look
    for this object's attributes."""

    # Create a new parser
    parser = optparse.OptionParser()

    # Add all options

    parser.add_option("-g","--ghost",
        action="store_true", dest="ghost", default=False,
        help="use ghost flying mode")

    return parser

# Parse options
parser = createOptionParser()
options, args = parser.parse_args()
setErrAction(options.verbose)
