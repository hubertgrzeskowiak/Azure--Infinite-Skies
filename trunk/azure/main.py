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

INSTRUCTIONS = """\
Azure testing ground
a/d - roll
w/s - pitch
q/e - yaw
z/c - move cam
x - reset cam

space - move forward
PageUp - increase thrust
PageDown - decrease thrust

VIEWS
p - first person
o - cockpit
i - third person
u - detached

ESC - quit
"""

import sys
import os
# Here panda will look for files with the ending .prc and load them as config.
# The config file will be loaded as soon as you touch a panda module.
p = ""
for i in os.getenv("PANDA_PRC_PATH").split(":"):
    p = i + ":"+ p
os.putenv("PANDA_PRC_PATH", p+"/etc/azure/:~/.azure/")
del p

try:
    from direct.showbase.ShowBase import ShowBase
    from direct.task import Task
except ImportError:
    print "It seems you haven't got Panda3D installed properly."
    sys.exit(1)


class Azure(object):
    """Main class called by the top level main function (see below)."""
    
    def __init__(self):
        """Only argument is the options object from the same named module."""

        ShowBase()
        base.disableMouse()

        from scenarios import TestEnvironment
        TestEnvironment()

        run()

if __name__ == "__main__":
    # issue with line ~53 where we set up PANDA_PRC_PATH
    print "Don't run this module directly! Use the run script instead!"
    sys.exit(2)
