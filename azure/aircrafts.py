"""This module manages everthing around loading, setting up and moving
aircrafts."""

import sys
import os
from math import cos, sin, radians, atan2, sqrt, pi, copysign, acos, asin, isnan
import ConfigParser

from pandac.PandaModules import ClockObject
from pandac.PandaModules import OdeBody, OdeMass, Quat
from direct.showbase.ShowBase import Plane, Vec3
from direct.actor.Actor import Actor
from direct.task import Task

from errors import *
from utils import ListInterpolator

_c = ClockObject.getGlobalClock()
specs = ConfigParser.SafeConfigParser()
specs.read(os.path.abspath(os.path.join(sys.path[0], "etc/CraftSpecs.cfg")))

class Aeroplane(object):
    """Standard aeroplane class."""

    _plane_count = 0
    aircrafts = None

    def __init__(self, name, model_to_load=None, specs_to_load=None,
            soundfile=None,world=None):
        """arguments:
        name -- aircraft name
        model_to_load -- model to load on init. same as name if none given.
                         0 = don't load a model
        specs_to_load -- specifications to load on init. same as name if none
                         given. 0 = don't load specs
        soundfile -- engine sound file (not yet implemented)
        world -- the physics world to connect to

        examples:   # load a plane called "corsair1" with model and specs "corsair"
                    pirate1 = Aeroplane("corsair1", "corsair")
                    # load an empty craft instance (you'll have to load model
                    # and specs later in turn to see or fly it)
                    foo = Aeroplane("myname", 0, 0)
                    # for the node itself, use:
                    foo = Aeroplane("bar")
                    airplane = foo.node
                    # if you need access to the model itself, use:
                    foo = Aeroplane("bar")
                    model = foo.node.getChild(0)

        info:       invisible planes are for tracking only. you should assign them
                    at least models when they get into visible-range.

                    The idea behind the 'node' is pretty simple: working with
                    a virtual container prevents accidential replacement and
                    seperates things.
        """

        if Aeroplane.aircrafts is None:
            assert render
            Aeroplane.aircrafts = render.attachNewNode("aircrafts")
        self.id = Aeroplane._plane_count
        Aeroplane._plane_count += 1

        self.node = Aeroplane.aircrafts.attachNewNode(
                                     "aeroplane {0} {1}".format(self.id, name))

        self.name = name
        self.model = None
        self.hud = None  # later replaced

        self.thrust = 0.0

        #try:
        #    self.model = self.loadPlaneModel(model_to_load)
        #    self.model.reparentTo(Aeroplane.aircrafts)
        #except (ResourceHandleError, ResourceLoadError, IOError), e:
        #    handleError(e)
        if not model_to_load:
            model_to_load = name
        self.model, self.animcontrols = self.loadPlaneModel(model_to_load)
        self.model.reparentTo(self.node)

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
        self.yaw_damping = -100
        self.pitch_damping = -100
        self.roll_damping = -100
        
        self.terminal_yaw = 3
        self.terminal_pitch = 3
        self.terminal_roll = 3
        
        self.rudder_coefficient = 1.0
        self.elevator_coefficient = 4.5
        self.ailerons_coefficient = 5.5
        
        self.pitch_force_coefficient = 4.0
        self.heading_force_coefficient = 1.0
        self.pitch_torque_coefficient = 0.1
        self.heading_torque_coefficient = 12.0
        
        # finally, complete initialisation of the physics for this plane
        if world is not None:
            # we are going to interact with the world :)
            body = OdeBody(world)
            # positions and orientation are set relative to render
            body.setPosition(self.node.getPos(render))
            body.setQuaternion(self.node.getQuat(render))
            
            mass = OdeMass()
            mass.setBox(self.mass, 1, 1, 1)
            body.setMass(mass)
            
            self.p_world = world
            self.p_body = body
            self.p_mass = mass
            
            self.accumulator = 0.0
            self.step_size = 0.02
            taskMgr.add(self.simulationTask,
                        "plane physics for {0}".format(self.name),
                        sort=-1,
                        taskChain="world")
            self.old_quat = self.quat()
        else:
            self.p_world = None
            self.p_body = None
            self.p_mass = None

        taskMgr.add(self._animations,
                    "plane animations for {0}".format(self.name),
                    sort=1,
                    taskChain="world")
        taskMgr.add(self._propellers,
                    "propellers animations for {0}".format(self.name),
                    sort=2,
                    taskChain="world")


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
                #animcontrols[anim] = actor.getAnimControls(anim, subpart, "mid", False)[0]
                animcontrols[anim] = actor.getAnimControls(anim, subpart, None, False)[0]
                
        actor.makeSubpart("propellers", "Propeller*")
        actor.verifySubpartsComplete()
        actor.setSubpartsComplete(True)
        self.propellers = []
        for p in actor.getJoints("propellers", "Propeller*", "lodRoot"):
            self.propellers.append(actor.controlJoint(None, "propellers", p.getName()))
        #actor.pprint()

        cams = model.findAllMatches("**/camera ?*")
        if not cams.isEmpty():
            cameras = actor.attachNewNode("cameras")
            cams.reparentTo(cameras)

        return actor, animcontrols

    def _animations(self, task):
        roll =  {-1: self.animcontrols["Roll Left"],
                  1: self.animcontrols["Roll Right"]}
        pitch = {-1: self.animcontrols["Pitch Down"],
                  1: self.animcontrols["Pitch Up"]}
        head =  {-1: self.animcontrols["Head Right"],
                  1: self.animcontrols["Head Left"]}
        for flaps, state in (
                (roll, self.ailerons),
                (pitch, self.elevator),
                (head, self.rudder)):
            if state == 0.0:
                for f in flaps:
                    if (flaps[f].isPlaying() == 1) and (flaps[f].getPlayRate() > 0):
                        flaps[f].setPlayRate(-1)
                    elif flaps[f].getFrame() == flaps[f].getNumFrames()-1:
                        if flaps[f].getPlayRate() > 0:
                            flaps[f].setPlayRate(-1)
                        flaps[f].play()
                    if (flaps[f].isPlaying() == 1) and (flaps[f].getFrame() == 0):
                        flaps[f].stop()
            else:
                if flaps[state*-1].isPlaying() == 1:
                    if flaps[state*-1].getPlayRate() > 0:
                        flaps[state*-1].setPlayRate(-1)
                    else:
                        if flaps[state*-1].getFrame() == 0:
                            flaps[state*-1].stop()
                else:
                    if flaps[state*-1].getFrame() == flaps[state*-1].getNumFrames()-1:
                        if flaps[state*-1].getPlayRate() > 0:
                            flaps[state*-1].setPlayRate(-1)
                        flaps[state*-1].play()
                    else:
                        if (flaps[state].isPlaying() == 0):
                            if not (flaps[state].getFrame() == (flaps[state].getNumFrames()-1)):
                                flaps[state].setPlayRate(1)
                                flaps[state].play()
                        elif flaps[state].getPlayRate() < 0:
                            flaps[state].setPlayRate(1)

        return Task.cont

    def _propellers(self, task):
        if self.thrust > 0:
            for p in self.propellers:
                p.setP(p, (self.thrust * _c.getDt() * 500))

        return Task.cont

    def loadSpecs(self, s, force=False):
        """Loads specifications for a plane. Force if already loaded."""

        def justLoad():
            self.mass = specs.getint(s, "mass")
            # 1km/h = 3.6 m/s (1meter = 1panda unit)
            self.max_speed = 3.6 * specs.getint(s, "max_speed")
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
    
    #def assignSound(self, soundfile):
    #    plane_sound = sound.Sound(soundfile, True, self.node)
    #    return plane_sound
    
    def move(self, movement):
        """Plane movement management."""
        if movement == "roll-left":
            self.ailerons = -1.0
        elif movement == "roll-right":
            self.ailerons = 1.0
        elif movement == "pitch-up":
            self.elevator = 1.0
        elif movement == "pitch-down":
            self.elevator = -1.0
        elif movement == "heading-left":
            self.rudder = 1.0
        elif movement == "heading-right":
            self.rudder = -1.0

    def chThrust(self, value):
        if value == "add" and self.thrust < 1.0:
            self.thrust += 0.01
        elif value == "subtract" and self.thrust > 0.0:
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
        
        return force
    
    def angleOfAttack(self):
        return self.angle_of_attack
    def gForceTotal(self):
        acc = self.acceleration - self.gravity/self.mass
        return acc.length()/9.81
    def gForce(self):
        up = self.node.getQuat().getUp()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(up) / 9.81
        return gf

    def lateralG(self):
        right = self.node.getQuat().getRight()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(right) / 9.81
        return gf

    def axialG(self):
        forward = self.node.getQuat().getForward()
        acc = self.acceleration - self.gravity/self.mass
        gf = acc.dot(forward) / 9.81
        return gf

    def velocity(self):
        """ return the current velocity """
        #return self.physics_object.getVelocity()
        return Vec3(self.p_body.getLinearVel())
    def setVelocity(self,v):
        self.p_body.setLinearVel(v)
    
    def angVelVector(self):
        """ return the current angular velocity as a vector """
        return self.p_body.getAngularVel()
    
    def angVelBodyHpr(self):
        """ return the heading, pitch and roll values about the body axis """
        angv = self.angVelVector()
        quat = self.quat()
        h = angv.dot(quat.getUp())
        p = angv.dot(quat.getRight())
        r = angv.dot(quat.getForward())
        return h,p,r
    
    def setAngularVelocity(self,v):
        self.p_body.setAngularVel(v)
    
    def speed(self):
        """ returns the current velocity """
        return self.velocity().length()
        
    def position(self):
        """ return the current position """
        return self.p_body.getPosition()
    def setPosition(self,p):
        self.p_body.setPosition(p)
    
    def altitude(self):
        """ returns the current altitude """
        return self.position().getZ()
    
    def quat(self):
        """ return the current quaternion representation of the attitude """
        return Quat(self.p_body.getQuaternion())
    
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
    
    def _controlRotForce(self,control,axis,coeff,speed,rspeed,max_rspeed):
        """ generic control rotation force
        control - positive or negative amount of elevator/rudder/ailerons
        axis - vector about which the torque is applied
        coeff - the conversion of the amount of the control to a rotational force
        speed - the speed of the plane
        rspeed - the current rotational speed about the axis
        max_rspeed - a cut-off for the rotational speed
        """
        if control * rspeed < max_rspeed:
            return axis * control * coeff * speed
        else:
            return Vec3(0.0,0.0,0.0)
    
    def _rotDamping(self,vector,rotv,damping_factor):
        """ generic damping """
        damp = damping_factor * rotv
        
        # rather than trusting that we have the sign right at any point
        # decide sign of the returned value based on the speed
        if rotv < 0.0:
            return vector * abs(damp)
        else:
            return vector * -abs(damp)
    
    def _forwardAndVelocityVectorForces(self,up,right,norm_v,speed):
        """ calculates torque and force resulting from deviation of the
        velocity vector from the forward vector """
        
        # could do with a better name for this method
        
        # get the projection of the normalised velocity onto the up and
        # right vectors to find relative pitch and heading angles
        p_angle = acos(up.dot(norm_v)) - pi/2
        h_angle = acos(right.dot(norm_v)) - pi/2
        
        torque_p = p_angle*self.pitch_torque_coefficient*speed
        torque_h = h_angle*self.heading_torque_coefficient*speed
        force_p = p_angle*self.pitch_force_coefficient*speed
        force_h = h_angle*self.heading_force_coefficient*speed
        
        return Vec3(-torque_p, 0.0, torque_h), Vec3(-force_p, 0.0, force_h)
    
    def simulationTask(self,task):
        """ update position and velocity based on aerodynamic forces """
        if self.p_world:
            self.accumulator += _c.getDt()
            while self.accumulator > self.step_size:
                self.accumulator -= self.step_size
                
                position = self.position()
                velocity = self.velocity()
                speed = velocity.length()
                norm_v = velocity + Vec3(0.0,0.0,0.0)
                norm_v.normalize()
                
                yawv,pitchv,rollv = self.angVelBodyHpr()
                
                quat = self.quat()
                forward = quat.getForward()
                up = quat.getUp()
                right = quat.getRight()
                
                linear_force = self._force(position,velocity,right,up,forward)
                
                self.p_body.addForce(linear_force)
                
                # Control forces:
                elevator_af = self._controlRotForce(self.elevator,Vec3(1.0,0.0,0.0),
                                                    self.elevator_coefficient,
                                                    speed,pitchv,self.terminal_pitch)
                ailerons_af = self._controlRotForce(self.ailerons,Vec3(0.0,1.0,0.0),
                                                    self.ailerons_coefficient,
                                                    speed,rollv,self.terminal_roll)
                rudder_af = self._controlRotForce(self.rudder,Vec3(0.0,0.0,1.0),
                                                    self.rudder_coefficient,
                                                    speed,yawv,self.terminal_yaw)
                
                # Damping forces
                pitch_damping_avf = self._rotDamping(Vec3(1.0,0.0,0.0),pitchv,self.pitch_damping)
                roll_damping_avf = self._rotDamping(Vec3(0.0,1.0,0.0),rollv,self.roll_damping)
                yaw_damping_avf = self._rotDamping(Vec3(0.0,0.0,1.0),yawv,self.yaw_damping)
                
                self.p_body.addRelTorque(elevator_af + ailerons_af + rudder_af +
                                         roll_damping_avf + pitch_damping_avf + yaw_damping_avf)
                
                # Forces to rotate the forward vector towards the velocity vector
                # and vice versa
                fvv_torque, fvv_force = self._forwardAndVelocityVectorForces(up,right,norm_v,speed)
                self.p_body.addRelTorque(fvv_torque)
                self.p_body.addForce(fvv_force)
                
                if position.getZ() < 0:
                    position.setZ(0)
                    velocity.setZ(0)
                    self.setPosition(position)
                    self.setVelocity(velocity)
                self.rudder = 0.0
                self.elevator = 0.0
                self.ailerons = 0.0
                self.p_world.quickStep(self.step_size)
            
            self.node.setPosQuat(render,self.position(),self.quat())
        return task.cont
