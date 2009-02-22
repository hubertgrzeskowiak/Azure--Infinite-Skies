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

INSTRUCTIONS = '''\
Azure testing ground
a/d - roll
w/s - pitch
q/e - yaw
z/c - move cam
x - reset cam

space - move forward
+/= - increase thrust
-   - decrease thrust

VIEWS
p - first person
o - cockpit
i - third person
u - detached

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
from optparse import OptionParser

# command line arguments now parsed prior to panda3d doing anything

# TODO: better management of arguments, especially verbosity and error
#       sensitivity

parser = OptionParser()

# constants for -v,-d and -q options are found in errors module
# so this module also needs to be loaded now.

from modules.errors import *

# TODO: decide and implement uniform custom module loading


parser.add_option('-v','--verbose',
                  action='store_const', const=RAISE, dest='verbose',
                  help='print extra information')
parser.add_option('-d','--debug',
                  action='store_const', const=DIE, dest='verbose',
                  help='print extra debugging information')
parser.add_option('-q','--quiet', 
                  action='store_const', const=IGNORE_ALL, dest='verbose',
                  help='do not print information')

# temporary flags to test camera modes and physics
parser.add_option('-p','--physicslevel', 
                  action='store', type="int",dest='physicslevel',
                  help='select physics model: 0 = off, 1 = basicphysics')
parser.add_option('-c','--enablecameramodes', 
                  action='store_true',dest='extracameramodes',default=False,
                  help='allow extra camera modes to be used')

parser.set_defaults(verbose=RAISE)
parser.set_defaults(physicslevel=0)

(options,args) = parser.parse_args()

setErrAction(options.verbose)

BASICPHYSICS = False
if options.physicslevel==1:
    BASICPHYSICS = True
EXTRACAMERAMODES = options.extracameramodes

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

from aircrafts import Aeroplane
from scenery import Scenery
from interface import printInstructions
#from errors import *
import views
#import controls
from controls import keyHandler, controlMap

# basic preperation
printInstructions(INSTRUCTIONS)
base.setBackgroundColor(0.0, 0.2, 0.3)
base.cam.node().getLens().setFar(1500)
base.disableMouse()

# a grey raster - for testing
from grid import Grid
G = Grid()
G.grid_node.setScale(10, 10, 10)

# load some scenery for testing the scenery backend module
scenery_obj = {}
scenery_obj['panda_green'] = Scenery('panda_green', 'environment', VBase3(0, 1000, 0))
#env_node = scenery_obj['panda_green'].dummy_node

# some lights
# TODO(Nemesis13): new module
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
if BASICPHYSICS: player.usebasicphysics=True

# load some dark ones, just for testing
planes['pirate1'] = Aeroplane('griffin')
pirate1 = planes['pirate1'].dummy_node
pirate1.setColor(0, 0, 1, 1)
pirate1.setPosHpr(-15, 20, 6, 230, 0, 0)

planes['pirate2'] = Aeroplane('griffin')
pirate2 = planes['pirate2'].dummy_node
pirate2.setColor(0, 0, 1, 1)
pirate2.setPosHpr(18, -30, 6, 20, 0, 0)

# set default camera
default_cam = views.PlaneCamera(player.dummy_node)
#default_cam.setViewMode(views.FIRST_PERSON)
#default_cam.setViewMode(views.DETACHED)
#default_cam.setViewMode(views.COCKPIT)

# now we can enable user input
#from controls import keyHandler, controlMap
ctlMap = controlMap()
k = keyHandler(ctlMap)

# TODO(Nemesis13): define what exactly belongs into this task and what should have own ones
def gameloop(task):
    for key, state in k.keyStates.items():
        if state == 1:
            keyInfo = ctlMap.controls[key]
            if keyInfo['type'] == 'move':
                planes['player'].move(keyInfo['desc'])
            elif keyInfo['type'] == 'cam-move':
                default_cam.rotate(keyInfo['desc'])
            elif keyInfo['type'] == 'cam-view' and EXTRACAMERAMODES:
                default_cam.setViewMode(keyInfo['desc'])
    #you should comment the line below to work with ghost mode
    if planes['player'].usebasicphysics:
        planes['player'].velocity() 
    default_cam.step()
    return Task.cont

gameTask = taskMgr.add(gameloop, 'gameloop')

# uncomment to view the rendering tree after exiting game
"""
print 80 * '-'
print render.ls()
print 80 * '-'
"""
run()
