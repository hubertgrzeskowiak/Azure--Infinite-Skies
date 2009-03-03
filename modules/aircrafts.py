"""this module manages everthing around loading, setting and moving
aircrafts"""

from math import cos, sin, radians, atan2, sqrt, pi

import ConfigParser
specs = ConfigParser.SafeConfigParser()
specs.read("etc/CraftSpecs.cfg")

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()
from direct.showbase.ShowBase import Plane, ShowBase, Vec3, Point3

from errors import *
from utils import ListInterpolator

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

        self.index = Aeroplane.plane_count
        Aeroplane.plane_count += 1

        new_node_name = "dummy_node" + str(Aeroplane.plane_count)
        self.dummy_node = aircrafts_cont.attachNewNode(new_node_name)
        
        self.thrust = 0
        self.thrust_scale = 5000
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
        
        # TODO (gjmm): these are specifications and should be moved to a file
        self.liftvsaoa = ListInterpolator([[radians(-10.0),-0.4],
                                           [radians(-8.0),-0.45],
                                           [radians(15.0),1.45],
                                           [radians(18.0),1.05]],
                                           0.0,0.0)
        self.dragvsaoa = ListInterpolator([[radians(-10.0),-0.010],
                                           [radians(0.0),0.006],
                                           [radians(4.0),0.005],
                                           [radians(8.0),0.0065],
                                           [radians(12.0),0.012],
                                           [radians(14.0),0.020],
                                           [radians(16.0),0.028]],
                                           0.03,0.1)
        self.lift_area = 49.2
        self.drag_area = 1.1
        self.drag_coef = 0.044
        self.drag_coef_x = 0.044
        self.drag_coef_y = 10.0
        self.drag_coef_z = 10.0
        self.drag_area_x = 20.0
        self.drag_area_y = 1.1
        self.drag_area_z = 20.0
        self.aspect_ratio = 8.0
        
        self.velocity_v = Vec3(0.0,0.0,0.0)
        self.heading_ang = 0.0
        self.setShortcutParameters()
    
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
    
    # (tomkis - two methods below -> rollback for keypressed event)
    def reverseRoll(self,offset=10.0):
        dt = c.getDt()
        roll = self.node().getR()
        
        # vary the rate depending on the angle out
        roll_factor = abs(roll/90.0)
        if roll_factor > 1:
            roll_factor = 2 - roll_factor
        roll_factor = sqrt(roll_factor) + 0.1
        
        if roll < -90.0 - offset:
            self.node().setR(node(), -1 * roll_factor * self.roll_speed * dt)
            if self.node().getR() > 0: self.node().setR(180.0)
        elif roll < 0.0:
            self.node().setR(self.node(), roll_factor * self.roll_speed * dt)
            if self.node().getR() > 0: self.node().setR(0.0)
        elif roll > 90.0 + offset:
            self.node().setR(self.node(), roll_factor * self.roll_speed * dt)
            if self.node().getR() < 0: self.node().setR(180.0)
        elif roll > 0.0:
            self.node().setR(self.node(), -1 * roll_factor * self.roll_speed * dt)
            if self.node().getR() < 0:
                self.node().setR(0.0)
    
    def reversePitch(self):
        dt = c.getDt()
        pitch = self.node().getP()
        
        # need this so that we know which direction to rotate
        if self.node().getQuat().getUp()[2] < 0:
            factor = -1
        else:
            factor = 1
        
        # vary the rate depending on the angle out
        pitch_factor = abs(pitch/90.0) + 0.1
        
        if pitch < 0.0:
            self.node().setP(self.node(), pitch_factor * factor * self.pitch_speed * dt)
            if self.node().getP() > 0: self.node().setP(0.0)
        elif pitch > 0.0:
            self.node().setP(self.node(), pitch_factor * factor * -1 * self.pitch_speed * dt)
            if self.node().getP() < 0: self.node().setP(0.0)
    
    def move(self, movement):
        """Plane movement management."""

        dt = c.getDt()
        
        # TODO (gjmm): modify the controls so that appropriately directed 
        #              rudder and elevator activated simultaneously gives a 
        #              coordinated turn?
        
        # TODO (gjmm): acceleration and decay of rotations from keyboard
        
        if movement == "roll-left":
            self.node().setR(self.node(), -1 * self.roll_speed * dt)
            #a=self.node().getR()
        if movement == "roll-right":
            self.node().setR(self.node(), self.roll_speed * dt)
            #b=self.node().getR()
        if movement == "pitch-up":
            self.node().setP(self.node(), self.pitch_speed * dt)
        if movement == "pitch-down":
            self.node().setP(self.node(), -1 * self.pitch_speed * dt)
        if movement == "heap-left":
            self.node().setH(self.node(), -1 * self.yaw_speed * dt)
        if movement == "heap-right":
            self.node().setH(self.node(), self.yaw_speed * dt)
        if movement == "move-forward":
            # 40 panda_units/s = ~12,4 km/h
            self.node().setFluidY(self.node(), 40 * dt)

    def chThrust(self, value):
        if value == "add" and self.thrust < 100: 
            self.thrust += 1
        if value == "subtract" and self.thrust > 0:
            self.thrust -= 1

    def setShortcutParameters(self):
        """pre-calculated flight parameters"""
        # density of air: rho = 1.2041 kg m-3
        half_rho = 0.602
        self.lift_factor = half_rho * self.lift_area
        
        # could modify lift_induced_drag by a factor of 1.05 to 1.15
        self.lift_induced_drag_factor = (-1.0) * self.lift_factor / \
                                        (pi*self.aspect_ratio)
        self.drag_factor_x = (-1.0) * half_rho * self.drag_area_x * self.drag_coef_x
        self.drag_factor_y = (-1.0) * half_rho * self.drag_area_y * self.drag_coef_y
        self.drag_factor_z = (-1.0) * half_rho * self.drag_area_z * self.drag_coef_z
        
        gravityscale = 10.0
        self.gravity = Vec3(0.0,0.0,(-9.81) * gravityscale * self.mass)
    
    def liftForce(self,v,v_squared,right,down,forward):
        """return the lift force vector generated by the wings"""
        # just make sure we are not modifying the external reference
        v = v + v.zero()
        
        # calculate the angle of attack in radians
        if v.normalize():
            projected_v = v - right * v.dot(right)
            aoa = atan2(projected_v.dot(down), projected_v.dot(forward))
        else:
            aoa = 0.0
        
        # lift direction is always perpendicular to the airflow
        lift_vector = right.cross(v)
        return lift_vector * v_squared * self.lift_factor * self.liftvsaoa[aoa]
    
    def liftInducedDragForce(self,v,v_squared):
        """return the drag force vector resulting from production of lift"""
        drag = v * sqrt(v_squared) * self.lift_induced_drag_factor
        return drag
    
    def simpleProfileDragForce(self,v,right,up,forward):
        """return the force vector due to the shape of the aircraft"""
        speed_x = right.dot(v)
        speed_y = forward.dot(v)
        speed_z = up.dot(v)
        
        drag_x = right*speed_x*speed_x*self.drag_factor_x
        drag_y = forward*speed_y*speed_y*self.drag_factor_y
        drag_z = up*speed_z*speed_z*self.drag_factor_z
        if speed_x < 0.0:
            drag_x = -drag_x
        if speed_y < 0.0:
            drag_y = -drag_y
        if speed_z < 0.0:
            drag_z = -drag_z
        return drag_x + drag_y + drag_z
        
    def thrustForce(self,thrust_vector):
        """return the force vector produced by the aircraft engines"""
        return thrust_vector * self.thrust * self.thrust_scale
    
    def velocityForces(self):
        """Update position based on basic forces model"""
        
        node = self.node()
        quat = node.getQuat()
        
        forward = quat.getForward()
        up = quat.getUp()
        right = quat.getRight()
        down = -up
        
        v = self.velocity_v
        v_squared = v.lengthSquared()
        
        # force calculations
        lift = self.liftForce(v,v_squared,right,down,forward)
        lift_induced_drag = self.liftInducedDragForce(v,v_squared)
        profile_drag = self.simpleProfileDragForce(v,right,up,forward)
        thrust = self.thrustForce(forward)
        
        force = lift + lift_induced_drag + profile_drag + self.gravity + thrust
        
        # if the plane is on the ground, the ground reacts to the downward force
        # TODO (gjmm): need to modify in order to consider reaction to objects
        #              at different altitudes.
        if node.getZ() == 0.0:
            if force[2] < 0.0:
                force.setZ(0.0)
                
        acceleration = force / self.mass
        
        dt = c.getDt()
        new_v = v + acceleration * dt
        
        node.setX(node.getX() + new_v[0] * dt)
        node.setY(node.getY() + new_v[1] * dt)
        node.setZ(node.getZ() + new_v[2] * dt)
        
        # correcting the height on touchdown or ground impact
        # TODO (gjmm): need to modify in order to consider objects at different
        #              altitudes.
        if node.getZ() < 0.0:
            node.setZ(0.0)
            new_v.setZ(0.0)
        
        # store the new velocity
        self.velocity_v = new_v
        
    def velocitySimple(self):
        """OLD ONE - Physical forces- and movement management."""
        dt = c.getDt()

        # coefficient for the lift force, I found it by experimentation
        # but it will be better to have an analytical solution
        self.k = 0.01
        
        self.pitch_ang = radians(self.node().getP())
        self.roll_ang = radians(self.node().getR())
        self.heap_ang = radians(self.node().getH())

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
        self.node().setFluidY(self.node(), self.thrust * dt)

        # this adds the gravity, it moves the plane at the direction of the
        # Z axis of the ground
        self.node().setZ(self.node().getZ() + self.gravity * dt * dt / 2)

        # this adds the movement at the z direction of the plane
        self.node().setFluidZ(self.node(), self.ForceZ*dt*dt/2/self.mass)

        # this makes the plane not to go below vertical 0
        if self.node().getZ() < 0:
            self.node().setZ(0)
        
        # TODO (gjmm): set velocity to real velocity
        self.velocity_v.setX(self.thrust*1.0)

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
