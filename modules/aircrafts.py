"""this module manages everthing around loading, setting and moving
aircrafts"""

from math import cos, sin, radians

import ConfigParser
specs = ConfigParser.SafeConfigParser()
specs.read("etc/CraftSpecs.cfg")

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

from errorHandler import *

# container for everything flying around
aircrafts_cont = render.attachNewNode("aircrafts_cont")

class Aeroplane(object):
    """Standard aeroplane class."""
    
    plane_count = 0

    def __init__(self, name, model_to_load=None, specs_to_load=None):
        """arguments:
        name -- aircraft name
        model_to_load -- model to load on init. same as name if none given.
                         0 = don't load a model
        specs_to_load -- specifications to load on init. same as name if none
                         given. 0 = don't load specs

        examples:   # load a plane called "corsair1" with model and specs "corsair"
                    pirate1 = Aeroplane("corsair1", "corsair")
                    # load an empty craft instance (you'll have to load model
                    # and specs later in turn to see or fly it)
                    foo = Aeroplane("myname", 0, 0)
                    # for the node itself, use:
                    foo = Aeroplane("bar").dummy_node
                    # if you need access to the model itself, use:
                    foo = Aeroplane("bar").plane_model
    
        info:       invisible planes are for tracking only. you should assign them
                    at least models    when they get into visible-range.
        """

        self.index = Aeroplane.plane_count
        Aeroplane.plane_count += 1

        new_node_name = "dummy_node" + str(Aeroplane.plane_count)
        self.dummy_node = aircrafts_cont.attachNewNode(new_node_name)
        
        self.usebasicphysics = False
        self.thrust = 0
        self.counter = 0

        if model_to_load == 0:
            pass
        elif model_to_load:
            try:
                self.loadPlaneModel(model_to_load)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)
        else:
            try:
                self.loadPlaneModel(name)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)

        if specs_to_load == 0:
            pass
        elif specs_to_load:
            self.loadSpecs(specs_to_load)
        else:
            self.loadSpecs(name)

    def loadPlaneModel(self, model, force=False):
        """Loads model for a plane. Force if there's already one loaded."""
        if hasattr(self, "plane_model"):
            if force:
                self.plane_model = loader.loadModel(model)
                if self.plane_model != None:
                    self.plane_model.reparentTo(self.dummy_node)
                else:
                    raise ResourceLoadError(model, "no such model")
            else:
                raise ResourceHandleError(
                    model, "aeroplane already has a model. force to change")
        else:
            self.plane_model = loader.loadModel(model)
            if self.plane_model:
                self.plane_model.reparentTo(self.dummy_node)
            else:
                raise ResourceLoadError(model, "no such model")

    def loadSpecs(self, s, force=False):
        """Loads specifications for a plane. Force if already loaded."""

        def justLoad():
            self.mass = specs.getint(s, "mass")
            # 1km/h = 2.7777 m/s (1meter = 1panda unit)
            self.max_speed = 2.7777 * specs.getint(s, "max_speed")
            self.roll_speed = specs.getint(s, "roll_speed")
            self.pitch_speed = specs.getint(s, "pitch_speed")
            self.yaw_speed = specs.getint(s, "yaw_speed")

        if hasattr(self, "specs"):
            if force:
                justLoad()
            else:
                print "craft already has specs assigned. force to change"
            self.specs = s
        else:
            justLoad()

    def move(self, movement):
        """Plane movement management."""

        dt = c.getDt()

        if movement == "roll-left":
            self.dummy_node.setR(self.dummy_node, -1 * self.roll_speed * dt)
        if movement == "roll-right":
            self.dummy_node.setR(self.dummy_node, self.roll_speed * dt)
        if movement == "pitch-up":
            self.dummy_node.setP(self.dummy_node, self.pitch_speed * dt)
        if movement == "pitch-down":
            self.dummy_node.setP(self.dummy_node, -1 * self.pitch_speed * dt)
        if movement == "heap-left":
            self.dummy_node.setH(self.dummy_node, -1 * self.yaw_speed * dt)
        if movement == "heap-right":
            self.dummy_node.setH(self.dummy_node, self.yaw_speed * dt)
        if movement == "move-forward":
            # 40 panda_units/s = ~12,4 km/h
            self.dummy_node.setFluidY(self.dummy_node, 40 * dt)
        if movement == "increase-thrust" and self.thrust < 100: 
            if self.usebasicphysics:
                self.thrust +=1 #increases the thrust
        if movement == "decrease-thrust"and self.thrust > 0:
            if self.usebasicphysics:
                self.thrust -=1

    def velocity(self):
        """Physical forces- and movement management."""
        dt = c.getDt()

        # coefficient for the lift force, I found it by experimentation
        # but it will be better to have an analytical solution
        self.k = 0.01
        
        self.pitch_ang = radians(self.dummy_node.getP())
        self.roll_ang = radians(self.dummy_node.getR())
        self.heap_ang = radians(self.dummy_node.getH())

        # acceleration of gravity but it was so small value so I multiplied
        # it with 500 also found by experimenting but will change after the
        # analytical solution
        self.gravity = -9.81 * 500

        # this force is to the z axis of the plane(not the relative axis),
        # so it does not have gravity but the thrust and the lift force,
        # 80000 is also an experimental value will change after the solution.
        self.ForceZ = (self.thrust * cos(self.heap_ang) +
            self.k * self.thrust * cos(self.roll_ang)) * 80000
        
         # this makes the plane go forward through its own axis
        self.dummy_node.setFluidY(self.dummy_node, self.thrust * dt)

        # this adds the gravity, it moves the plane at the direction of the
        # Z axis of the ground
        self.dummy_node.setZ(self.dummy_node.getZ() + self.gravity * dt * dt / 2)

        # this adds the movement at the z direction of the plane
        self.dummy_node.setFluidZ(self.dummy_node, self.ForceZ*dt*dt/2/self.mass)

        # this makes the plane not to go below vertical 0
        if self.dummy_node.getZ() < 0:
            self.dummy_node.setZ(0)

    def getBounds(self):
        """Returns a vector describing the vehicle's size (width, length,
        height). Useful for collision detection."""
        bounds = self.dummy_node.getTightBounds()
        size = bounds[1] - bounds[0]
        return size
