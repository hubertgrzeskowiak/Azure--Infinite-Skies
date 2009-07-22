#!/usr/bin/env python
"""
Azure: Infinite Skies

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

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import sys
import os

from direct.showbase.ShowBase import ShowBase
# init panda's hi-level backend (declares some builtins)
ShowBase()
from pandac.PandaModules import loadPrcFileData
from direct.showbase.DirectObject import DirectObject
#from direct.showbase.Messenger import Messenger
from direct.task import Task
from direct.directtools.DirectGrid import DirectGrid
#from direct.gui.DirectGui import OnscreenText
#from pandac.PandaModules import TextNode
from pandac.PandaModules import VBase3, Vec4
from pandac.PandaModules import AmbientLight,DirectionalLight
#from pandac.PandaModules import ClockObject
#c = ClockObject.getGlobalClock()

import options
import gui
import views
import controls
from aircrafts import Aeroplane
from scenery import Scenery, setSky

#------------------------------------------------------------------------------
# Settings
#------------------------------------------------------------------------------

# will be moved to xml files
loadPrcFileData('', 'model-path $MAIN_DIR/assets')
#loadPrcFileData('', 'sync-video 0')  # disable framerate limitation
#loadPrcFileData('', 'want-directtools #t')
#loadPrcFileData('', 'want-tk #t')
#loadPrcFileData('', 'fullscreen #t')
#loadPrcFileData('', 'show-frame-rate-meter 1')  # display framerate


#------------------------------------------------------------------------------
# Main Azure Class
#------------------------------------------------------------------------------

class Azure(object):
    """Main class called by the top level main function (see below)."""
    
    def __init__(self, options):
        """Only argument is the options object from the same named module."""

        self.options = options
        self.hud = None
        self.planes = None
        self.defaultCam = None
        self.ControlsMap = None
        self.k = None
            
        self.initPanda3dEngine()

    def startGame(self):
        """Main starting function. Begin the loop."""

        gameTask = taskMgr.add(self.gameloop, 'gameloop')

        # start all the panda3D internal tasks (from DirectStart)
        run()
    
#------------------------------------------------------------------------------

    def initPanda3dEngine(self):
        """Inits all settings and objects for Panda3D."""
        
        # basic preperation
        gui.printInstructions(INSTRUCTIONS)
        base.setBackgroundColor(0.0, 0.2, 0.3)
        base.cam.node().getLens().setFar(10000)
        #base.camLens.setFar(10000)
        base.disableMouse()

        # a grey raster - for testing
        DG = DirectGrid(2000, 20, parent=render)

        # load some scenery for testing the scenery module
        #scenery_obj = {}
        #scenery_obj["panda_green"] = Scenery("panda_green", "environment", VBase3(0, 1000, 0))

        # set up a nice skybox
        setSky("bluesky")

        # some lights
        # TODO(Nemesis13): new module
        dlight = DirectionalLight("dlight")
        alight = AmbientLight("alight")
        dlnp = render.attachNewNode(dlight.upcastToPandaNode()) 
        alnp = render.attachNewNode(alight.upcastToPandaNode())
        dlight.setColor(Vec4(1.0, 0.9, 0.8, 1))
        alight.setColor(Vec4(0.6, 0.6, 0.8, 1))
        dlnp.setP(-60) 
        render.setLight(dlnp)
        render.setLight(alnp)

        # load our plane(s)
        self.planes = {}
        self.player = self.planes["player"] = Aeroplane("griffin")

        # load some dark ones, just for testing
        self.planes["pirate1"] = Aeroplane("griffin")
        pirate1 = self.planes["pirate1"].node()
        pirate1.setColor(0, 0, 1, 1)
        pirate1.setPosHpr(-15, 20, 6, 230, 0, 0)

        self.planes["pirate2"] = Aeroplane("griffin")
        pirate2 = self.planes["pirate2"].node()
        pirate2.setColor(0, 0, 1, 1)
        pirate2.setPosHpr(18, -30, 6, 20, 0, 0)

        # set default camera
        self.defaultCam = views.PlaneCamera(self.player.dummy_node)
        #default_cam.setViewMode(views.FIRST_PERSON)
        #default_cam.setViewMode(views.DETACHED)
        #default_cam.setViewMode(views.COCKPIT)

        # now we can enable user input
        self.ControlsMap = controls.ControlsMap()
        self.k = controls.KeyHandler(self.ControlsMap)

        self.hud = gui.HUD(self.player, self.defaultCam)
        
#------------------------------------------------------------------------------

    # TODO(Nemesis13): define what exactly belongs into
    # this task and what should have own ones
    def gameloop(self, task):
        """This task is run every frame."""

        active_motion_controls = []
        
        for key, state in self.k.keyStates.items():
            if state == 1:
                keyInfo = self.ControlsMap.controls[key]
                if keyInfo["type"] == "move":
                    #self.player.move(keyInfo["desc"])
                    if not self.options.ghost:
                        active_motion_controls.append(keyInfo["desc"])
                if self.options.ghost:
                    if keyInfo["type"] == "ghost-move":
                        self.player.move(keyInfo["desc"])
                elif keyInfo["type"] == "thrust":
                    self.player.chThrust(keyInfo["desc"])
                elif keyInfo["type"] == "cam-move":
                    self.player.move(keyInfo["desc"])
                elif keyInfo["type"] == "cam-move":
                    self.defaultCam.rotate(keyInfo["desc"])
                elif keyInfo["type"] == "cam-view":
                    self.defaultCam.setViewMode(keyInfo["desc"])
        
        if self.options.autolevel and len(active_motion_controls) == 2:
            if all(x in active_motion_controls for x in ("roll-left", "roll-right")):
                self.player.reverseRoll()
            elif all(x in active_motion_controls for x in ("pitch-down", "pitch-up")):
                self.player.reversePitch()
            else:
                for movement in active_motion_controls:
                    self.player.move(movement)
        else:
            for movement in active_motion_controls:
                self.player.move(movement)

        if not self.options.ghost:             
            if self.options.oldphysics:
                self.player.velocitySimple()
            else:
                self.player.velocityForces() 

        self.defaultCam.step()
        self.hud.update()
        return Task.cont
        
#------------------------------------------------------------------------------
# Main Function
#------------------------------------------------------------------------------

def main():
    
    # Create new azure object
    azure = Azure(options.options)
    azure.startGame()

if __name__ == "__main__":
    main()
