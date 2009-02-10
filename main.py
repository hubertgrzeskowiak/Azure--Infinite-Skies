#!/usr/bin/env python
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
a/d - roll
w/s - pitch
q/e - yaw
z/c - move cam
x - reset cam

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
from pandac.PandaModules import VBase3, Vec4
from pandac.PandaModules import AmbientLight,DirectionalLight
from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

# assures that if module is called from another directory, all
# references still work
os.chdir(sys.path[0])

# custom modules
sys.path.append('modules')
from aeroplaneBackend import Aeroplane
from sceneryBackend import scenery
from interface import printInstructions
from errorHandler import *
import camBackend

# check for args and set verbosity/error-sensitivity

# TODO: better management of arguments, especially verbosity and error
#       sensitivity
# TODO: use the getopt module
setErrAction(RAISE)
#setErrAction(QUIET)
for arg in sys.argv[1:]:
	print arg
	if arg in ('--verbose', '-v'):
		setErrAction(RAISE)
	elif arg in ('--debug', '-d'):
		setErrAction(DIE)
		#messenger.toggleVerbose()
	elif arg in ('--quiet', '-q'):
		setErrAction(IGNORE_ALL)
	else:
		print('Unrecognized argument: %s' % arg)
		sys.exit(1)

# basic preperation
printInstructions(instructions)
base.setBackgroundColor(0.0, 0.2, 0.3)
base.cam.node().getLens().setFar(1500)
base.disableMouse()

# a grey raster - for testing
from grid import Grid
G = Grid()
G.grid_node.setScale(10, 10, 10)

# load some scenery for testing the sceneryBackend
scenery_obj = {}
scenery_obj['panda_green'] = scenery('panda_green', 'environment', VBase3(0, 1000, 0))
#env_node = scenery_obj['panda_green'].dummy_node

# some lights
# TODO: new module(?)
dlight = DirectionalLight('dlight')
alight = AmbientLight('alight')
dlnp = render.attachNewNode(dlight.upcastToPandaNode()) 
alnp = render.attachNewNode(alight.upcastToPandaNode())
dlight.setColor(Vec4(1.0, 0.9, 0.8, 1))
alight.setColor(Vec4(0.6, 0.6, 0.8, 1))
dlnp.setP(-60) 
render.setLight(dlnp)
render.setLight(alnp)

# load our plane(s)
planes = {}
player = planes['player'] = Aeroplane('griffin')

# TODO: Work on camBackend module
default_cam = camBackend.PlaneCamera(player.dummy_node)
#default_cam.setViewMode(camBackend.FIRST_PERSON)
#default_cam.setViewMode(camBackend.DETACHED)
#default_cam.setViewMode(camBackend.COCKPIT)

# load some dark ones, just for testing
planes['pirate1'] = Aeroplane('griffin')
pirate1 = planes['pirate1'].dummy_node
pirate1.setColor(0, 0, 1, 1)
pirate1.setPosHpr(-15, 20, 6, 230, 0, 0)

planes['pirate2'] = Aeroplane('griffin')
pirate2 = planes['pirate2'].dummy_node
pirate2.setColor(0, 0, 1, 1)
pirate2.setPosHpr(18, -30, 6, 20, 0, 0)

# now we can enable user input
from keyHandler import keyHandler, controlMap
ctlMap = controlMap()
k = keyHandler(ctlMap)

# here comes the magic!
# TODO: define what exactly belongs into this task and what should have own ones
def gameloop(task):
	for key, state in k.keyStates.items():
		if state == 1:
			keyInfo = ctlMap.controls[key]
			if keyInfo['type'] == 'move':
				planes['player'].move(keyInfo['desc'])
			elif keyInfo['type'] == 'cam-move':
				default_cam.rotate(keyInfo['desc'])
	default_cam.step()
	return Task.cont

gameTask = taskMgr.add(gameloop, 'gameloop')

# depending on verbosity level
'''
print 80 * '-'
print render.ls()
print 80 * '-'
'''
run()
