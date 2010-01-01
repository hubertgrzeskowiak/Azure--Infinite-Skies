"""This module manages everthing around loading, setting up and moving
aircrafts."""

from math import cos, sin, radians, atan2, sqrt, pi
import ConfigParser
from pandac.PandaModules import ClockObject
from pandac.PandaModules import PandaNode, NodePath, ActorNode
from pandac.PandaModules import ForceNode, AngularVectorForce, LinearVectorForce
from pandac.PandaModules import AngularEulerIntegrator

from direct.showbase.ShowBase import Plane, ShowBase, Vec3, Point3, LRotationf
from errors import *
from utils import ListInterpolator
#import sound

_c = ClockObject.getGlobalClock()
specs = ConfigParser.SafeConfigParser()
specs.read("etc/CraftSpecs.cfg")

class Aeroplane(object):
    """Standard aeroplane class."""

    _plane_count = 0

    def __init__(self, name, model_to_load=None, specs_to_load=None,
            soundfile=None):
        """arguments:
        name -- aircraft name
        model_to_load -- model to load on init. same as name if none given.
                         0 = don't load a model
        specs_to_load -- specifications to load on init. same as name if none
                         given. 0 = don't load specs
        soundfile -- engine sound file (not yet implemented)

        examples:   # load a plane called "corsair1" with model and specs "corsair"
                    pirate1 = Aeroplane("corsair1", "corsair")
                    # load an empty craft instance (you'll have to load model
                    # and specs later in turn to see or fly it)
                    foo = Aeroplane("myname", 0, 0)
                    # for the node itself, use:
                    foo = Aeroplane("bar")
                    airplane = foo.node()
                    # if you need access to the model itself, use:
                    foo = Aeroplane("bar")
                    model = foo.node().getChild(0)

        info:       invisible planes are for tracking only. you should assign them
                    at least models when they get into visible-range.

                    The idea behind the node() is pretty simple: working with
                    a virtual container prevents accidential replacement and
                    seperates things.
        """

        if not hasattr(Aeroplane, "_aircrafts"):
            assert render
            Aeroplane._aircrafts = render.attachNewNode("aircrafts")
        self._id = Aeroplane._plane_count
        Aeroplane._plane_count += 1

        new_node_name = "aeroplane" + str(Aeroplane._plane_count)
        new_physics_node_name = "%s-physics" % new_node_name
        
        self._dummy_node = Aeroplane._aircrafts.attachNewNode(new_node_name)
        del new_node_name
        self.name = name

        self.thrust = 0.0

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
        
        # add new objects associated with the physics
        Node=NodePath(PandaNode(new_physics_node_name))
        Node.reparentTo(render)

        self.plane_model.reparentTo(self._dummy_node)
        self.actor_node=ActorNode("plane-physics")
        self.anp=Node.attachNewNode(self.actor_node)
        base.physicsMgr.attachPhysicalNode(self.actor_node)
        self._dummy_node.reparentTo(self.anp)
        Node.reparentTo(Aeroplane._aircrafts)
        self.physics_object = self.actor_node.getPhysicsObject()
        
        angleInt = AngularEulerIntegrator()
        base.physicsMgr.attachAngularIntegrator(angleInt)
        
        if specs_to_load == 0:
            pass
        elif specs_to_load:
            self.loadSpecs(specs_to_load)
        else:
            self.loadSpecs(name)
        
        """
        if soundfile == 0:
            pass
        elif soundfile:
            self.assignSound(soundfile)
        else:
            self.assignSound(name)
        """

        # precalculated values for combinations of variables
        self.setCalculationConstants()

        # dynamic variables
        self.acceleration = Vec3(0.0,0.0,0.0)
        self.angle_of_attack = 0.0
        
        # state variables
        self.rudder = 0.0
        self.ailerons = 0.0
        self.elevator = 0.0
        
        # more parameters
        self.yaw_damping = -1000
        self.pitch_damping = -500
        self.roll_damping = -100
        
        self.terminal_yaw = 0.0005
        self.terminal_pitch = 0.001
        self.terminal_roll = 0.002
        
        self.rudder_coefficient = 0.1
        self.elevator_coefficient = 1.5
        self.ailerons_coefficient = 1.5
    
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
            self.plane_model = loader.loadModel("planes/" + model + "/" + model)
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

        # TODO (gjmm): these are specifications and should be moved to a file

        self.wing_area = 48.0 # m^2
        self.wing_span = 24.0 # m

        self.drag_coef_x = 0.9
        self.drag_coef_y = 0.1
        self.drag_coef_z = 0.9
        self.drag_area_x = 30.0
        self.drag_area_y = 2.75
        self.drag_area_z = 50.0
        self.aspect_ratio = self.wing_span * self.wing_span /self.wing_area

        self.liftvsaoa = ListInterpolator([[radians(-10.0),-0.4],
                                           [radians(-8.0),-0.45],
                                           [radians(15.0),1.75],
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
        self.max_thrust = 5000.0
        physics_object = self.actor_node.getPhysicsObject()
        physics_object.setMass(self.mass)
        #physics_object.setVelocity(Vec3(0,200,0))
        #physics_object.setPosition(Point3(0,-100,10000))
    
    #def assignSound(self, soundfile):
    #    plane_sound = sound.Sound(soundfile, True, self.node())
    #    return plane_sound
    
    def move(self, movement):
        """Plane movement management."""
        if movement == "roll-left":
            self.ailerons = -1.0
        if movement == "roll-right":
            self.ailerons = 1.0
        if movement == "pitch-up":
            self.elevator = 1.0
        if movement == "pitch-down":
            self.elevator = -1.0
        if movement == "heading-left":
            self.rudder = 1.0
        if movement == "heading-right":
            self.rudder = -1.0

    def chThrust(self, value):
        if value == "add" and self.thrust < 1.0:
            self.thrust += 0.01
        if value == "subtract" and self.thrust > 0.0:
            self.thrust -= 0.01

    def setCalculationConstants(self):
        """pre-calculate some calculation constants from the
        flight parameters"""
        # density of air: rho = 1.2041 kg m-3
        half_rho = 0.602
        self.lift_factor = half_rho * self.wing_area

        # could modify lift_induced_drag by a factor of 1.05 to 1.15
        self.lift_induced_drag_factor = (-1.0) * self.lift_factor / \
                                        (pi*self.aspect_ratio)
        self.drag_factor_x = (-1.0) * half_rho * self.drag_area_x * \
                                                 self.drag_coef_x
        self.drag_factor_y = (-1.0) * half_rho * self.drag_area_y * \
                                                 self.drag_coef_y
        self.drag_factor_z = (-1.0) * half_rho * self.drag_area_z * \
                                                 self.drag_coef_z

        self.gravity = Vec3(0.0,0.0,(-9.81) * self.mass)

    def _wingAngleOfAttack(self,v_norm,up):
        """ calculate the angle between the wing and the relative motion of the air """

        #projected_v = v_norm - right * v_norm.dot(right)
        #aoa = atan2(projected_v.dot(-up), projected_v.dot(forward))
        #return aoa

        # strangely enough, the above gets the same result as the below
        # for these vectors it must be calculating the angle in the plane where
        # right is the normal vector

        return v_norm.angleRad(up) - pi/2.0


    def _lift(self,v_norm,v_squared,right,aoa):
        """return the lift force vector generated by the wings"""
        # lift direction is always perpendicular to the airflow
        lift_vector = right.cross(v_norm)
        return lift_vector * v_squared * self.lift_factor * self.liftvsaoa[aoa]

    def _drag(self,v,v_squared,right,up,forward,aoa):
        """return the drag force"""

        # get the induced drag coefficient
        # Cdi = (Cl*Cl)/(pi*AR*e)

        lift_coef = self.liftvsaoa[aoa]
        ind_drag_coef = lift_coef * lift_coef / (pi * self.aspect_ratio * 1.10)

        # and calculate the drag induced by the creation of lift
        induced_drag =  -v * sqrt(v_squared) * self.lift_factor * ind_drag_coef
        #induced_drag = Vec3(0.0,0.0,0.0)
        profile_drag = self._simpleProfileDrag(v,right,up,forward)

        return induced_drag + profile_drag

    def _simpleProfileDrag(self,v,right,up,forward):
        """return the force vector due to the shape of the aircraft"""
        speed_x = right.dot(v)
        speed_y = forward.dot(v)
        speed_z = up.dot(v)

        drag_x = right*speed_x*abs(speed_x)*self.drag_factor_x
        drag_y = forward*speed_y*abs(speed_y)*self.drag_factor_y
        drag_z = up*speed_z*abs(speed_z)*self.drag_factor_z
        return drag_x + drag_y + drag_z

    def _thrust(self,thrust_vector):
        """return the force vector produced by the aircraft engines"""
        return thrust_vector * self.thrust * self.max_thrust

    def _force(self,p,v,right,up,forward):
        """calculate the forces due to the velocity and orientation of the aircraft"""
        v_squared = v.lengthSquared()
        v_norm = v + v.zero()
        v_norm.normalize()

        aoa = self._wingAngleOfAttack(v_norm,up)
        lift = self._lift(v_norm,v_squared,right,aoa)
        drag = self._drag(v,v_squared,right,up,forward,aoa)
        thrust = self._thrust(forward)
        self.angle_of_attack = aoa

        force = lift + drag + self.gravity + thrust

        # if the plane is on the ground, the ground reacts to the downward force
        # TODO (gjmm): need to modify in order to consider reaction to objects
        #              at different altitudes.
        if p.getZ() == 0.0:
            if force[2] < 0.0:
                force.setZ(0.0)
        
        lvf = LinearVectorForce(force)
        lvf.setMassDependent(1)
        return lvf
    
    
    
    def angleOfAttack(self):
        return self.angle_of_attack
    def gForceTotal(self):
        acc = self.acceleration - self.gravity/self.mass
        return acc.length()/9.81
    def gForce(self):
        up = self.node().getQuat().getUp()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(up) / 9.81
        return gf

    def lateralG(self):
        right = self.node().getQuat().getRight()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(right) / 9.81
        return gf

    def axialG(self):
        forward = self.node().getQuat().getForward()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(forward) / 9.81
        return gf
    
    def id(self):
        """Every plane has its own unique ID."""
        return self._id

    def node(self):
        """Returns the plane's dummy node (empty node it's parented to)."""
        return self._dummy_node
    
    def velocity(self):
        """ return the current velocity """
        return self.physics_object.getVelocity()
    
    def angularVelocity(self):
        """ return the current angular velocity """
        return self.physics_object.getRotation()
    def setAngularVelocity(self,ang_vel):
        self.physics_object.setRotation(ang_vel)
    
    def speed(self):
        """ returns the current velocity """
        return self.velocity().length()
        
    def position(self):
        """ return the current position """
        return self.physics_object.getPosition()
    
    def altitude(self):
        """ returns the current altitude """
        return self.position().getZ()
    
    def quat(self):
        """ return the current quaternion representation of the attitude """
        return self.physics_object.getOrientation()
    
    def info(self):
        velocity = self.velocity()
        position = self.position()
        quat = self.quat()
        heading,pitch,roll = quat.getHpr()
        return dict(velocity = velocity,
                    speed = velocity.length(),
                    climb_rate = velocity.getZ(),
                    position = position,
                    height = position.getZ(),
                    quat = quat,
                    heading = heading,
                    pitch = pitch,
                    roll = roll)
    
    def _rudderAF(self,speed,yaw_v):
        """ angular force from rudder """
        if self.rudder * yaw_v < self.terminal_yaw:
            return AngularVectorForce(self.rudder * self.rudder_coefficient * speed, 0.0, 0.0)
        else:
            return AngularVectorForce(0.0, 0.0, 0.0)
    def _elevatorAF(self,speed,pitch_v):
        """ angular force from elevator """
        if self.elevator * pitch_v < self.terminal_pitch:
            return AngularVectorForce(0.0, self.elevator * self.elevator_coefficient * speed, 0.0)
        else:
            return AngularVectorForce(0.0, 0.0, 0.0)
    def _aileronsAF(self,speed,roll_v):
        """ angular force from elevator """
        if self.ailerons * roll_v < self.terminal_roll:
            return AngularVectorForce(0.0, 0.0, self.ailerons * self.ailerons_coefficient * speed)
        else:
            return AngularVectorForce(0.0, 0.0, 0.0)
    
    def _genDamp(self,v,damping_factor):
        """ generic damping """
        damp = damping_factor * v
        
        # rather than trusting that we have the sign right at any point
        # decide sign of the returned value based on the speed
        if v < 0.0:
            return abs(damp)
        else:
            return -abs(damp)
    
    def _yawDampingAF(self,yaw_v):
        """ damp the current yaw based on the current yaw rate """
        return AngularVectorForce(self._genDamp(yaw_v,self.yaw_damping), 0.0, 0.0)
    def _pitchDampingAF(self,pitch_v):
        """ damp the current pitch based on the current pitch rate """
        return AngularVectorForce(0.0, self._genDamp(pitch_v,self.pitch_damping), 0.0)
    def _rollDampingAF(self,roll_v):
        """ damp the current pitch based on the current pitch rate """
        return AngularVectorForce(0.0, 0.0, self._genDamp(roll_v,self.roll_damping))
        
    
    def runDynamics(self):
        """ update position and velocity based on aerodynamic forces """
        # Reset the dynamics
        actor_physical = self.actor_node.getPhysical(0)
        actor_physical.clearLinearForces()
        
        # Collect the required quantities from the physics object
        physics_object = self.physics_object
        
        position = self.position()
        velocity = self.velocity()
        speed = velocity.length()
        
        angular_velocity = self.angularVelocity()
        dummy,pitchv,rollv,yawv = self.angularVelocity()
        
        quat = self.quat()        
        forward = quat.getForward()
        up = quat.getUp()
        right = quat.getRight()
        
        all_lvf = self._force(position,velocity,right,up,forward)
        
        forceNode=ForceNode('aeroplane-forces')
        forceNode.addForce(all_lvf)
        actor_physical.addLinearForce(all_lvf)
        
        # Add transverse control angular forces
        rudder_avf = self._rudderAF(speed,yawv)
        elevator_avf = self._elevatorAF(speed,pitchv)
        actor_physical.addAngularForce(rudder_avf)
        actor_physical.addAngularForce(elevator_avf)
        
        # Add transverse rotational damping forces
        yaw_damping_avf = self._yawDampingAF(yawv)
        pitch_damping_avf = self._pitchDampingAF(pitchv)
        actor_physical.addAngularForce(yaw_damping_avf)
        actor_physical.addAngularForce(pitch_damping_avf)
        
        # Add axial control angular forces
        ailerons_avf = self._aileronsAF(speed,rollv)
        actor_physical.addAngularForce(ailerons_avf)
        
        roll_damping_avf = self._rollDampingAF(rollv)
        actor_physical.addAngularForce(roll_damping_avf)
        
        # Apply rotational damping forces
        
        if position.getZ() < 0:
            position.setZ(0)
            velocity.setZ(0)
            physics_object.setPosition(position)
            physics_object.setVelocity(velocity)
        self.rudder = 0.0
        self.elevator = 0.0
        self.ailerons = 0.0
            
