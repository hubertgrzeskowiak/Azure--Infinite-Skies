"""This module manages everthing around loading, setting up and moving
aircrafts."""

import sys
import os
#import ConfigParser

from pandac.PandaModules import ClockObject
from pandac.PandaModules import NodePath
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.task import Task

from azure.errors import *
from azure.physics import AeroplanePhysics

#specs = ConfigParser.SafeConfigParser()
#specs.read(os.path.abspath(os.path.join(sys.path[0], "etc/CraftSpecs.cfg")))

global_clock = ClockObject.getGlobalClock()

class Aeroplane(DirectObject):
    """Standard aeroplane class."""

    def __init__(self, name, model=None, physics=False):
        """Arguments:
        name -- Aircraft name.

        model -- Model to load on init. Same as name if none given.
                 A string with the name of a plane in assets/planes/ is
                 expected.
                 0 or False = don't load a model

        physics -- When True, makes this plane physical.

        info:       invisible planes (without model) are for tracking only.
                    you should assign them models when they get into
                    visible range.

                    The idea behind the 'node' is pretty simple: working with
                    a virtual container prevents accidential replacement and
                    seperates things.
        """
        self.node = NodePath("aeroplane "+name)

        self.name = name
        self.model = None
        self.animcontrols = None
        self.hud = None
        self.ailerons = 0.0
        self.elevator = 0.0
        self.rudder = 0.0
        self.propellers = []

        if model is None:
            model = name
        if model:
            self.model, self.animcontrols = self.loadPlaneModel(model)
            self.model.reparentTo(self.node)

        self.physics = None
        if physics:
            self.activatePhysics();

    def loadPlaneModel(self, modelname):
        """Loads models and animations from the planes directory."""
        animcontrols = {}
        model = loader.loadModel("planes/{0}/{0}".format(modelname))
        actor = Actor(model, setFinal=True, mergeLODBundles=True,
                      allowAsyncBind=False, okMissing=False)
        #actor = Actor(model, lodNode="mid")

        subparts = (
        # subpart,       joints,                   animations
        ("Doors",        ["Windscreen*", "Door*"], ("Open", "Close")),
        #("Landing Gear", ["Landing?Gear*", "LG*"], ("LG Out", "LG In")),
        ("Landing Gear", ["Landing?Gear*", "LG*"], ("LG Out",)),
        ("Ailerons",     ["Aileron*"],            ("Roll Left", "Roll Right")),
        ("Rudders",      ["Rudder*"],             ("Head Left", "Head Right")),
        ("Elevators",    ["Elevator*"],           ("Pitch Up", "Pitch Down"))
        )

        for line in subparts:
            subpart, joints, anims = line
            actor.makeSubpart(subpart, joints)

            path = "planes/{0}/{0}-{{0}}".format(modelname)
            d = dict((anim, path.format(anim)) for anim in anims)

            #actor.loadAnims(d, subpart, "mid")
            actor.loadAnims(d, subpart)
            for anim in anims:
                #actor.bindAnim(anim, subpart, "mid")
                actor.bindAnim(anim, subpart)
                #animcontrols[anim] = actor.getAnimControls(anim, subpart,
                #                                           "mid", False)[0]
                animcontrols[anim] = actor.getAnimControls(anim, subpart,
                                                               None, False)[0]
        actor.makeSubpart("propellers", "Propeller*")
        actor.verifySubpartsComplete()
        actor.setSubpartsComplete(True)
        for p in actor.getJoints("propellers", "Propeller*", "lodRoot"):
            self.propellers.append(actor.controlJoint(None, "propellers",
                                                                 p.getName()))
        #actor.pprint()

        cams = model.findAllMatches("**/camera ?*")
        if not cams.isEmpty():
            cameras = actor.attachNewNode("cameras")
            cams.reparentTo(cameras)

        return actor, animcontrols

    def activatePhysics(self):
        if self.physics is not None:
            return 1
        self.physics = AeroplanePhysics(self.node)
        self.addTask(self._propellers,
                     "propeller animations",
                     taskChain="world")
        self.addTask(self._flapAnimations,
                     "flaps animations")

    def deactivatePhysics(self):
        if self.physics is None:
            return 1
        self.physics.destroy()
        self.physics = None
        self.removeTask(self._propellers)
        self.removeTask(self._flapAnimations)

    def _flapAnimations(self, task):
        if self.physics is None:
            return 1

        roll =  {-1: self.animcontrols["Roll Left"],
                  1: self.animcontrols["Roll Right"]}
        pitch = {-1: self.animcontrols["Pitch Down"],
                  1: self.animcontrols["Pitch Up"]}
        head =  {-1: self.animcontrols["Head Right"],
                  1: self.animcontrols["Head Left"]}
        for flaps, state in (
                (roll, self.physics.ailerons),
                (pitch, self.physics.elevator),
                (head, self.physics.rudder)):
            if state == 0.0:
                for f in flaps:
                    if (flaps[f].isPlaying() == 1) and \
                       (flaps[f].getPlayRate() > 0):
                        flaps[f].setPlayRate(-1)
                    elif flaps[f].getFrame() == flaps[f].getNumFrames()-1:
                        if flaps[f].getPlayRate() > 0:
                            flaps[f].setPlayRate(-1)
                        flaps[f].play()
                    if (flaps[f].isPlaying() == 1) and \
                       (flaps[f].getFrame() == 0):
                        flaps[f].stop()
            else:
                if flaps[state*-1].isPlaying() == 1:
                    if flaps[state*-1].getPlayRate() > 0:
                        flaps[state*-1].setPlayRate(-1)
                    else:
                        if flaps[state*-1].getFrame() == 0:
                            flaps[state*-1].stop()
                else:
                    if flaps[state*-1].getFrame() == \
                                             flaps[state*-1].getNumFrames()-1:
                        if flaps[state*-1].getPlayRate() > 0:
                            flaps[state*-1].setPlayRate(-1)
                        flaps[state*-1].play()
                    else:
                        if (flaps[state].isPlaying() == 0):
                            if not (flaps[state].getFrame() == \
                                             (flaps[state].getNumFrames()-1)):
                                flaps[state].setPlayRate(1)
                                flaps[state].play()
                        elif flaps[state].getPlayRate() < 0:
                            flaps[state].setPlayRate(1)

        return Task.cont

    def _propellers(self, task):
        if self.physics is None:
            return 1
        if self.physics.thrust > 0:
            delta_time = global_clock.getDt()
            for p in self.propellers:
                p.setP(p, (self.physics.thrust * delta_time * 500))
        return Task.cont

    def __str__(self):
		return self.name

    def __repr__(self):
		r =  "Aeroplane {}\n"
		r += "model: {}\n"
		r += "physics: {}\n"
		r = r.format(self.name, self.model, self.physics)
		return r

# Test
if __name__ == "__main__":
    from direct.showbase.ShowBase import ShowBase
    ShowBase()
    a = Aeroplane("test plane", False)
    print a.__repr__()
