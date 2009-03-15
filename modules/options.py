import optparse

# constants for -v,-d and -q options are found in errors module
from modules.errors import *

def createOptionParser():
    "Creates a the parser object an return it"
    
    # Create a new parser
    parser = optparse.OptionParser()

    # Add all options
    parser.add_option("-v", "--verbose", action = "store_const", const = RAISE,             
        dest = "verbose", help = "print extra information")
    parser.set_defaults(verbose = RAISE)
    
    parser.add_option("-d","--debug", action = "store_const", const = DIE,
        dest = "verbose", help = "print extra debugging information")
        
    parser.add_option("-q","--quiet", action = "store_const", 
        const = IGNORE_ALL, dest = "verbose", 
        help = "do not print information")

    # temporary flags to test camera modes and physics
    parser.add_option("-g","--ghost", 
        action="store_true", dest="ghost", default=False,
        help="use ghost flying mode")
    parser.add_option("-o","--oldphysics", 
        action="store_true", dest="oldphysics", default=False,
        help="use old physics")
    parser.add_option("-a","--autolevel", 
        action="store_true", dest="autolevel", default=False,
        help="allow autolevel code")

    
    return parser

# Parse options
parser = createOptionParser()
options, args = parser.parse_args()
setErrAction(options.verbose)
