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
# Here panda will look for files with the ending .prc and load them as config.
# The config file will be loaded as soon as you touch a panda module.
#os.putenv("PANDA_PRC_PATH", "./etc/:../etc/:/etc/azure/:~/.azure/")
# Ffor now, load only our development config. First 2 lines are old-style,
# latter 2 for panda 1.7 and above.
os.environ["PANDA_PRC_DIR"] = os.getcwd()
os.environ["PANDA_PRC_PATH"] = os.getcwd()
os.environ["PRC_DIR"] = os.getcwd()
os.environ["PRC_PATH"] = os.getcwd()

try:
    from pandac.PandaModules import loadPrcFile
except ImportError:
    print "It seems you haven't got Panda3D installed properly."
    sys.exit(1)
# Just for the case setting the environment variable setting failed, load the
# config file now. It can'T overwrite everything from the beginning anymore,
# but should work well as a fallback.
loadPrcFile("etc/azure.prc")


from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *


class Azure(object):
    """Main class called by the top level main function (see below)."""

    def __init__(self):
        """Only argument is the options object from the same named module."""

        ShowBase()
        #base.disableMouse()

        from scenarios import TestEnvironment
        TestEnvironment()

        run()

# Related to relative paths.
if __name__ == "__main__":
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
