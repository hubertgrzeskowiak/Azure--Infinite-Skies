"""this module manages everthing around loading, setting and moving
aircrafts"""

from math import cos, sin, radians, atan2, sqrt, pi

import ConfigParser

from pandac.PandaModules import ClockObject
from direct.showbase.ShowBase import Plane, ShowBase, Vec3, Point3

from errors import *
from utils import ListInterpolator
from flight import FlightDynamicsModel

DEF_CONTROLS = {'pitch-up':False,
                'pitch-down':False,
                'pitch-autolevel':False,
                'roll-left':False,
                'roll-right':False,
                'roll-autolevel':False,
                'heap-left':False,
                'heap-right':False,
               }

c = ClockObject.getGlobalClock()

specs = ConfigParser.SafeConfigParser()
specs.read("etc/CraftSpecs.cfg")

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
                    foo = Aeroplane("bar").node()
                    # if you need access to the model itself, use:
                    foo = Aeroplane("bar").plane_model
    
        info:       invisible planes are for tracking only. you should assign them
                    at least models when they get into visible-range.

                    The idea behind the node() is pretty simple: working with
                    a virtual container prevents accidential replacement and
                    seperates things.
        """
        
        self.fdm = FlightDynamicsModel()
        
        self.index = Aeroplane.plane_count
        Aeroplane.plane_count += 1

        new_node_name = "dummy_node" + str(Aeroplane.plane_count)
        self.dummy_node = aircrafts_cont.attachNewNode(new_node_name)
        
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
        
        # dynamic variables
        velocity = Vec3(0.0,0.0,0.0)
        acceleration = Vec3(0.0,0.0,0.0)
        angle_of_attack = 0.0
        self.fdm.loadDynamicVariables(v=velocity,a=acceleration,
                            alpha=angle_of_attack)
        
        # precalculated values for combinations of variables
        self.fdm.resetCalculationConstants()
    
    def loadPlaneModel(self, model, force=False):
        """Loads model for a plane. Force if there's already one loaded."""
        if hasattr(self, "plane_model"):
            if force:
                self.plane_model = loader.loadModel(model)
                if self.plane_model != None:
                    self.plane_model.reparentTo(self.node())
                else:
                    raise ResourceLoadError(model, "no such model")
            else:
                raise ResourceHandleError(
                    model, "aeroplane already has a model. force to change")
        else:
            self.plane_model = loader.loadModel(model)
            if self.plane_model:
                self.plane_model.reparentTo(self.node())
            else:
                raise ResourceLoadError(model, "no such model")

    def loadSpecs(self, s, force=False):
        """Loads specifications for a plane. Force if already loaded."""
        spec_dict = {}
        
        def justLoad():
            temp_dict = {}
            temp_dict["unloaded_mass"] = specs.getint(s, "mass")
            # 1km/h = 2.7777 m/s (1meter = 1panda unit)
            temp_dict["max_speed"] = 2.7777 * specs.getint(s, "max_speed")
            temp_dict["roll_speed"] = specs.getint(s, "roll_speed")
            temp_dict["pitch_speed"] = specs.getint(s, "pitch_speed")
            temp_dict["yaw_speed"] = specs.getint(s, "yaw_speed")
            return temp_dict

        if hasattr(self, "specs"):
            if force:
                temp_dict = justLoad()
            else:
                temp_dict = {}
                print "craft already has specs assigned. force to change"
            self.specs = s
        else:
            temp_dict = justLoad()
        
        # TODO (gjmm): these are specifications and should be moved to a file
        wing_area = 48.0 # m^2
        wing_span = 24.0 # m
        spec_dict["wing_area"] = wing_area
        spec_dict["wing_span"] = wing_span
        spec_dict["drag_coefs"] = [0.9,0.1,0.9]
        spec_dict["drag_areas"] = [30.0,2.75,50.0]
        spec_dict["aspect_ratio"] = wing_span * wing_span / wing_area
        spec_dict["lift_vs_alpha"] = ListInterpolator([[radians(-18.0),-1.05],
                                           [radians(-15.0),-1.75],
                                           [radians(15.0),1.75],
                                           [radians(18.0),1.05]],
                                           0.0,0.0)
        # drag_vs_alpha not loaded
        spec_dict["drag_vs_alpha"] = ListInterpolator([[radians(-10.0),-0.010],
                                           [radians(0.0),0.006],
                                           [radians(4.0),0.005],
                                           [radians(8.0),0.0065],
                                           [radians(12.0),0.012],
                                           [radians(14.0),0.020],
                                           [radians(16.0),0.028]],
                                           0.03,0.1)
        spec_dict["max_thrust"] = 5000.0
        
        self.fdm.loadSpecs(**spec_dict)
    
    def reverseRoll(self,offset=10.0):
        """Automatically levels the airplane in the roll axis
        The offset argument allows the airplane to level to upright flight
        when the initial roll vector is beyond 90 degrees.
        """
        # local copies of the relevant data
        dt = c.getDt()
        roll = self.node().getR()
        
        # This may not be strictly necessary but this causes the roll rate
        # to decrease as the roll approaches the target angle
        r_factor = abs(roll/90.0)
        if r_factor > 1:
            # we are upside down and so the factor is reversed (offset ignored)
            r_factor = 2 - r_factor
        # sqrt gives a decaying effect, constant allows target to be reached
        r_factor = sqrt(r_factor) + 0.1
        
        # Determine the quadrant and apply the appropriate rotation,
        #       correcting if the target is overshot
        if roll < -90.0 - offset:
            self.node().setR(self.node(), -1 * r_factor * self.roll_speed * dt)
            if self.node().getR() > 0: 
                self.node().setR(180.0)
        elif roll < 0.0:
            self.node().setR(self.node(), r_factor * self.roll_speed * dt)
            if self.node().getR() > 0: 
                self.node().setR(0.0)
        elif roll > 90.0 + offset:
            self.node().setR(self.node(), r_factor * self.roll_speed * dt)
            if self.node().getR() < 0: 
                self.node().setR(180.0)
        elif roll > 0.0:
            self.node().setR(self.node(), -1 * r_factor * self.roll_speed * dt)
            if self.node().getR() < 0:
                self.node().setR(0.0)
    
    def reversePitch(self):
        """Automatically levels the airplane in the pitch axis"""
        # local copies of the relevant data
        dt = c.getDt()
        pitch = self.node().getP()
        
        # The angular range for pitch is -90 -> 90 and so we need extra
        # information to determine the direction to rotate:
        if self.node().getQuat().getUp()[2] < 0:
            factor = -1
        else:
            factor = 1
        
        # This may not be strictly necessary but this causes the roll rate
        # to decrease as the roll approaches the target angle
        p_factor = abs(pitch/90.0) + 0.1
        # sqrt gives a decaying effect, constant allows target to be reached
        p_factor = sqrt(p_factor) + 0.1
        
        # Determine the quadrant, helped by the 'factor' calculated above,
        # and apply the appropriate rotation; correct if the target is overshot
        if pitch < 0.0:
            self.node().setP(self.node(), p_factor * factor * \
                                                     self.pitch_speed * dt)
            if self.node().getP() > 0: self.node().setP(0.0)
        elif pitch > 0.0:
            self.node().setP(self.node(), -1 * p_factor * factor * \
                                                     self.pitch_speed * dt)
            if self.node().getP() < 0: self.node().setP(0.0)
    
    def applyControls(self,controls):
        """ management of keyboard movement requests """
        cntrls = {}
        cntrls.update(DEF_CONTROLS)
        cntrls.update(controls)
        [self.move(ctrl) for ctrl,v in cntrls.iteritems() if v]
        
        dt = c.getDt()
        
        if cntrls["pitch-up"]:
            self.fdm.applyControl(0,1.0,dt)
        elif cntrls["pitch-down"]:
            self.fdm.applyControl(0,-1.0,dt)
        elif cntrls["pitch-autolevel"]:
            # do this in place of auto-levelling for now
            self.fdm.centreControl(0,dt)
        else:
            self.fdm.centreControl(0,dt)
        
        if cntrls["roll-left"]:
            self.fdm.applyControl(1,-1.0,dt)
        elif cntrls["roll-right"]:
            self.fdm.applyControl(1,1.0,dt)
        elif cntrls["roll-autolevel"]:
            # do this in place of auto-levelling for now
            self.fdm.centreControl(1,dt)
        else:
            self.fdm.centreControl(1,dt)
        
        if cntrls["heap-left"]:
            self.fdm.applyControl(2,-1.0,dt)
        elif cntrls["heap-right"]:
            self.fdm.applyControl(2,1.0,dt)
        else:
            self.fdm.centreControl(2,dt)
    
    def move(self, movement):
        """Plane movement management."""

        dt = c.getDt()
        
        # TODO (gjmm): modify the controls so that appropriately directed 
        #              rudder and elevator activated simultaneously gives a 
        #              coordinated turn?
        
        # TODO (gjmm): acceleration and decay of rotations from keyboard
        
        if movement == "roll-left":
            self.node().setR(self.node(), -1 * self.fdm.roll_speed * dt)
            #a=self.node().getR()
        if movement == "roll-right":
            self.node().setR(self.node(), self.fdm.roll_speed * dt)
            #b=self.node().getR()
        if movement == "pitch-up":
            self.node().setP(self.node(), self.fdm.pitch_speed * dt)
        if movement == "pitch-down":
            self.node().setP(self.node(), -1 * self.fdm.pitch_speed * dt)
        if movement == "heap-left":
            self.node().setH(self.node(), -1 * self.fdm.yaw_speed * dt)
        if movement == "heap-right":
            self.node().setH(self.node(), self.fdm.yaw_speed * dt)
        if movement == "move-forward":
            # 40 panda_units/s = ~12,4 km/h
            self.node().setFluidY(self.node(), 40 * dt)
    
    def chThrust(self, value):
        if value == "add" and self.fdm.dyn_vars.thrust_perc < 1.0: 
            self.fdm.dyn_vars.thrust_perc += 0.01
        if value == "subtract" and self.fdm.dyn_vars.thrust_perc > 0.0:
            self.fdm.dyn_vars.thrust_perc -= 0.01
    
    def speed(self):
        """ returns the current velocity """
        return self.fdm.dyn_vars.speed
    def altitude(self):
        """ returns the current altitude """
        return self.fdm.dyn_vars.altitude
    
    def velocityForces(self):
        """Update position based on basic forces model"""
        
        # collect together the appropriate information
        node = self.node()
        self.fdm.dyn_vars.loadFromPandaNode(node)
        self.fdm.dyn_vars.calcDerivedValues()
        quat = node.getQuat()
        
        # and the timestep
        dt = c.getDt()
        p,v,a = self.fdm.dyn_vars.getPVA()
        ang_p,ang_v,ang_a = self.fdm.dyn_vars.getAngularPVA()
        new_p,new_v,new_a = self.fdm.modVelocityVerletInt(self.fdm.dyn_vars,
                                              p,v,a,
                                              self.fdm.linearA,dt)
        new_ang_p,new_ang_v,new_ang_a = \
                            self.fdm.modVelocityVerletInt(self.fdm.dyn_vars,
                                              ang_p,ang_v,ang_a,
                                              self.fdm.rotationalA,dt)
        
        if new_p.getZ() < 0.0:
            new_p.setZ(0.0)
            new_v.setZ(0.0)
        
        # store the new position, velocity and acceleration
        self.fdm.dyn_vars.setPVA(new_p,new_v,new_a)
        self.fdm.dyn_vars.setAngularPVA(new_ang_p,new_ang_v,new_ang_a)
        
        self.fdm.dyn_vars.exportToPandaNode(node)
    
    def angleOfAttack(self):
        return self.fdm.dyn_vars.alpha
    def gForceTotal(self):
        acc = self.fdm.dyn_vars.a - self.fdm.gravity/self.fdm.dyn_vars.m
        return acc.length()/9.81
    def gForce(self):
        acc = fdm.dyn_vars.a - self.fdm.gravity/self.fdm.dyn_vars.m
        gf = acc.dot(self.fdm.dyn_vars.up) / 9.81
        return gf
    
    def lateralG(self):
        acc = self.fdm.dyn_vars.a - self.gravity/self.fdm.dyn_vars.m
        gf = acc.dot(self.fdm.dyn_vars.ri) / 9.81
        return gf
    
    def axialG(self):
        acc = self.fdm.dyn_vars.a - self.gravity/self.fdm.dyn_vars.m
        gf = acc.dot(self.fdm.dynvars.fw) / 9.81
        return gf
    
    def velocitySimple(self):
        """OLD ONE - Physical forces- and movement management."""
        dt = c.getDt()
        
        l_thrust = self.thrust * self.max_speed

        # coefficient for the lift force, I found it by experimentation
        # but it will be better to have an analytical solution
        self.k = 0.01
        
        self.pitch_ang = radians(self.node().getP())
        self.roll_ang = radians(self.node().getR())
        self.heap_ang = radians(self.node().getH())

        # acceleration of gravity but it was so small value so I multiplied
        # it with 500 also found by experimenting but will change after the
        # analytical solution
        
        self.gravity_scalar = -9.81 * 500

        # this force is to the z axis of the plane(not the relative axis),
        # so it does not have gravity but the thrust and the lift force,
        # 80000 is also an experimental value will change after the solution.
        self.ForceZ = (l_thrust * cos(self.heap_ang) +
            self.k * l_thrust * cos(self.roll_ang)) * 80000
        
         # this makes the plane go forward through its own axis
        self.node().setFluidY(self.node(), l_thrust * dt)

        # this adds the gravity, it moves the plane at the direction of the
        # Z axis of the ground
        self.node().setZ(self.node().getZ() + self.gravity_scalar*dt*dt/2.0)

        # this adds the movement at the z direction of the plane
        self.node().setFluidZ(self.node(), self.ForceZ*dt*dt/2.0/self.mass)

        # this makes the plane not to go below vertical 0
        if self.node().getZ() < 0:
            self.node().setZ(0)
        
        # TODO (gjmm): set velocity to real velocity
        self.velocity.setX(l_thrust)

    def bounds(self):
        """Returns a vector describing the vehicle's size (width, length,
        height). Useful for collision detection."""
        bounds = self.node().getTightBounds()
        size = bounds[1] - bounds[0]
        return size

    def node(self):
        """Returns the plane's container. Please use this instead of
        dummy_node or the actual model."""
        return self.dummy_node
