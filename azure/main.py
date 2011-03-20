import sys
import os

try:
    from pandac.PandaModules import loadPrcFile
    from pandac.PandaModules import Filename
except ImportError:
    print "It seems you haven't got Panda3D installed properly."
    sys.exit(1)
# Config file should be loaded as soon as possible.
# TODO(Nemesis#13): this must get smarter
loadPrcFile(Filename.fromOsSpecific(os.path.abspath(os.path.join(sys.path[0], "etc/azure.prc"))))
from direct.showbase.ShowBase import ShowBase

from core import Core
import options


class Azure(ShowBase):
    """Main class called by the top level main function (see below)."""
    def __init__(self):
        if options.print_version:
            try:
                print open("VERSION").read()
            except IOError:
                print "Version unknown. Can't find the VERSION file."
            sys.exit()

        # This basically sets up our rendering node-tree, some builtins and
        # the master loop (which iterates each frame).
        ShowBase.__init__(self)
        # Turn off Panda3D's standard camera handling.
        self.disableMouse()
        self.setBackgroundColor(0,0,0,1)
        # Start our Finite State Machine
        if options.scenario:
            self.core = Core(options.scenario)
        else:
            self.core = Core()

        #base.bufferViewer.toggleEnable()
		# Start the master loop.
        self.run()

# Related to relative paths.
if __name__ == "__main__":
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
