"""Azure: Infinite Skies main file. This module handles a few command line
options and starts the core finite state machine, followed by Panda's task
manager."""

import sys
import os

# Set Python Path to the directory this file lies in
sys.path[0] = os.path.dirname(os.path.abspath(__file__))

try:
    import panda3d
except ImportError:
    print "It seems you haven't got Panda3D installed properly."
    sys.exit(1)

from panda3d.core import ExecutionEnvironment as EE
from panda3d.core import Filename
from options import options

# If we only need to print version, do this first and leave everything else
# untouched.
if options.print_version:
    try:
        f = Filename(EE.expandString("$MAIN_DIR/VERSION")).toOsSpecific()
        print open(f).read()
    except IOError:
        print "Version unknown. Can't find the VERSION file."
    sys.exit()

from pandac.PandaModules import loadPrcFile
from pandac.PandaModules import Filename
# Config file should be loaded as soon as possible.
loadPrcFile(EE.expandString("$MAIN_DIR/etc/azure.prc"))
from direct.showbase.ShowBase import ShowBase

from core import Core


class Azure(ShowBase):
    def __init__(self):
        """Program entry point."""
        # TODO(Nemesis#13): rewrite ShowBase to not use globals.

        # This basically sets up our rendering node-tree, some builtins and
        # the master loop (which iterates each frame).
        ShowBase.__init__(self)

        # Turn off Panda3D's standard camera handling.
        self.disableMouse()

        self.setBackgroundColor(0,0,0,1)

        # Start our Core Finite State Machine
        self.core = Core()
        if (options.scenario):
            # Scenario was specified at command line.
            self.core.demand("Loading", options.scenario)
        else:
            self.core.demand("Menu", "MainMenu")

        #base.bufferViewer.toggleEnable()

		# Start the master loop.
        self.run()

if __name__ == "__main__":
    # Related to relative paths.
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
