#!/usr/bin/python
'''
Azure: Infinite Skies

Copyright (C) 2009 Hubert Grzeskowiak

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
'''

instructions = '''\
Azure testing ground
a - roll left
d - roll right
w - pitch down
s - pitch up
q - yaw left
e - yaw right
space - move forward
ESC - quit
'''

# some configuration settings
from pandac.PandaModules import loadPrcFileData
loadPrcFileData('', 'model-path $MAIN_DIR/models')
# let's see how many FPS we can get maximal
#loadPrcFileData('', 'sync-video 0')
# some cool control tools
#loadPrcFileData('', 'want-directtools #t')
#loadPrcFileData('', 'want-tk #t')
#loadPrcFileData('', 'fullscreen #t')

# python standard modules
import sys, os

# panda3d modules
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.showbase.Messenger import Messenger
from direct.task import Task
from direct.gui.DirectGui import OnscreenText
from pandac.PandaModules import TextNode
from pandac.PandaModules import ClockObject
from pandac.PandaModules import VBase3
c = ClockObject.getGlobalClock()

# assures that if module is called from another directory, all
# references still work
os.chdir(sys.path[0])

# custom modules
sys.path.append('modules')
from aeroplaneBackend import aeroplane
from sceneryBackend import scenery
from interface import printInstructions

# check for args
for arg in  sys.argv:
	if arg == ('--verbose' or '-v'):
		verbose = 1
	elif arg == ('--debug' or '-d'):
		verbose = 2
		messenger.toggleVerbose()
	elif arg == ('--quiet' or '-q'):
		verbose = -1
	else:
		verbose = 0

# basic preperation
printInstructions(instructions)
base.setBackgroundColor(0.0, 0.2, 0.3)
baselens = base.cam.node().getLens().setFar(1500)
base.camera.setHpr(0, -16, 0)
base.camera.setPos(0, -25, 12)
base.disableMouse()

# a grey raster - for testing
from grid import grid
g = grid()
g.grid_node.setScale(10, 10, 10)

# load some scenery for testing the sceneryBackend
scenery_obj = {}
scenery_obj['panda_green'] = scenery('panda_green', 'environment', VBase3(0, 1000, 0))
#env_node = scenery_obj['panda_green'].dummy_node


# load our plane(s)
planes = {}
player = planes['player'] = aeroplane('griffin')

# TODO: entire new module is needed for camera movement
base.camera.reparentTo(player.dummy_node)

# load some dark ones, just for testing
planes['pirate1'] = aeroplane('griffin')
pirate1 = planes['pirate1'].dummy_node
pirate1.setColor(0, 0, 1, 1)
pirate1.setPosHpr(-15, 20, 6, 230, 0, 0)

planes['pirate2'] = aeroplane('griffin')
pirate2 = planes['pirate2'].dummy_node
pirate2.setColor(0, 0, 1, 1)
pirate2.setPosHpr(18, -30, 6, 20, 0, 0)

# now we can enable user input
from keyHandler import keyHandler
k = keyHandler()

# here comes the magic!
def gameloop(task):
	for key in k.keyStates.items():
		if key[1] == 1:
			planes['player'].move(key[0])
	# comment out the reparenting above and uncomment this to get another view
	#base.cam.lookAt(player.dummy_node)
	return Task.cont

gameTask = taskMgr.add(gameloop, 'gameloop')

if verbose >= 1:
	print 80 * '-'
	print render.ls()
	print 80 * '-'

run()
