#!/usr/bin/env python

"""Azure: Infinite Skies

Copyright (c) 2009 Azure Developers

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.
"""

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


class Azure(object):
    """Main class called by the top level main function (see below)."""
    def __init__(self):

        # This basically sets up our rendering node-tree, some builtins and
        # the master loop (which iterates each frame).
        ShowBase()
        # Turn off Panda3D's standard camera handling.
        #base.disableMouse()
        base.setBackgroundColor(0,0,0,1)
        base.core = Core()
		# Start the master loop.
        #base.bufferViewer.toggleEnable()
        run()


# Related to relative paths.
if __name__ == "__main__":
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
