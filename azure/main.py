import sys
import os
try:
    from pandac.PandaModules import loadPrcFile
    from pandac.PandaModules import Filename
except ImportError:
    print "It seems you haven't got Panda3D installed properly."
    sys.exit(1)
# Config file should be loaded as soon as possible.
loadPrcFile(Filename.fromOsSpecific(os.path.abspath(os.path.join(sys.path[0], "etc/azure.prc"))))
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

from core import Core


class Azure(ShowBase):
    """Main class called by the top level main function (see below)."""
    def __init__(self):

        # This basically sets up our rendering node-tree, some builtins and
        # the master loop (which iterates each frame).
        ShowBase.__init__(self)
        # Turn off Panda3D's standard camera handling.
        self.disableMouse()
        self.setBackgroundColor(0,0,0,1)
        self.core = Core()
		# Start the master loop.
        #base.bufferViewer.toggleEnable()
        self.run()

# Related to relative paths.
if __name__ == "__main__":
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
