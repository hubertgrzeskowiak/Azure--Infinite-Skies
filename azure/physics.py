"""This module manages everthing around loading, setting up and moving
aircrafts."""

import sys
import os
from math import cos, sin, radians, atan2, sqrt, pi, copysign, acos, asin, isnan
import ConfigParser

from pandac.PandaModules import ClockObject
from pandac.PandaModules import OdeBody, OdeMass, Quat, OdeWorld
from direct.showbase.ShowBase import Plane, Vec3
from direct.actor.Actor import Actor
from direct.task import Task

from errors import *
from utils import ListInterpolator

#specs = ConfigParser.SafeConfigParser()
#specs.read(os.path.abspath(os.path.join(sys.path[0], "etc/CraftSpecs.cfg")))
global_clock = ClockObject.getGlobalClock()


class Physical(object):
    world = OdeWorld()
    world.setGravity(0,0,0)

    def __init__(self):
        self.world = Physical.world


class AeroplanePhysics(Physical):
    def __init__(self, node):

        Physical.__init__(self)

        self.node = node
        self.thrust = 0.0
        self.loadSpecs()

        # precalculated values for combinations of variables
        self.setCalculationConstants()

        # dynamic variables
        self.acceleration = Vec3(0.0,0.0,0.0)
        self.angle_of_attack = 0.0
        
        # state variables
        self.rudder = 0.0
        self.ailerons = 0.0
        self.elevator = 0.0
        
        
        self.ode_body = OdeBody(self.world)
        # positions and orientation are set relative to render
        self.ode_body.setPosition(self.node.getPos(render))
        self.ode_body.setQuaternion(self.node.getQuat(render))
        
        self.ode_mass = OdeMass()
        self.ode_mass.setBox(self.mass, 1, 1, 1)
        self.ode_body.setMass(self.ode_mass)
        
        self.accumulator = 0.0
        self.step_size = 0.02
        taskMgr.add(self.simulationTask,
                    "plane physics",
                    sort=-1,
                    taskChain="world")

    def loadSpecs(self):
        """Loads specifications for a plane. Force if already loaded."""

        # TODO (gjmm): these are specifications and should be moved to a file

        self.mass = 1000
        self.max_thrust = 5000.0

        self.wing_area = 48.0 # m^2
        self.wing_span = 24.0 # m

        self.drag_coef_x = 0.9
        self.drag_coef_y = 0.1
        self.drag_coef_z = 0.9
        self.drag_area_x = 30.0
        self.drag_area_y = 2.75
        self.drag_area_z = 50.0
        self.aspect_ratio = self.wing_span * self.wing_span /self.wing_area

        # What the hell is this?! I still don't get it... :-(
        # Does this need to be individual per plane?
        # -Nemesis13
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
        delta_time = global_clock.getDt()
        if value == "add" and self.thrust < 1.0:
            self.thrust += 0.01
        elif value == "subtract" and self.thrust > 0.0:
            self.thrust -= 0.01

    def getThrust(self):
        return self.thrust

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

        self.gravity = Vec3(0.0,0.0,-9.81) 
        self.gravityM = self.gravity * self.mass

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

        force = lift + drag + self.gravityM + thrust

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
        acc = self.acceleration - self.gravity
        return acc.length()/9.81
    def gForce(self):
        up = self.node.getQuat().getUp()
        acc = self.acceleration - self.gravity
        gf = acc.dot(up) / 9.81
        return gf

    def lateralG(self):
        right = self.node.getQuat().getRight()
        acc = self.acceleration - self.gravity
        gf = acc.dot(right) / 9.81
        return gf

    def axialG(self):
        forward = self.node.getQuat().getForward()
        acc = self.acceleration - self.gravity
        gf = acc.dot(forward) / 9.81
        return gf

    def velocity(self):
        """ return the current velocity """
        #return self.physics_object.getVelocity()
        return Vec3(self.ode_body.getLinearVel())
    def setVelocity(self,v):
        self.ode_body.setLinearVel(v)
    
    def angVelVector(self):
        """ return the current angular velocity as a vector """
        return self.ode_body.getAngularVel()
    
    def angVelBodyHpr(self):
        """ return the heading, pitch and roll values about the body axis """
        angv = self.angVelVector()
        quat = self.quat()
        h = angv.dot(quat.getUp())
        p = angv.dot(quat.getRight())
        r = angv.dot(quat.getForward())
        return h,p,r
    
    def setAngularVelocity(self,v):
        self.ode_body.setAngularVel(v)
    
    def speed(self):
        """ returns the current velocity """
        return self.velocity().length()
        
    def position(self):
        """ return the current position """
        return self.ode_body.getPosition()
    def setPosition(self,p):
        self.ode_body.setPosition(p)
    
    def altitude(self):
        """ returns the current altitude """
        return self.position().getZ()
    
    def quat(self):
        """ return the current quaternion representation of the attitude """
        return Quat(self.ode_body.getQuaternion())
    
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
        """Update position and velocity based on aerodynamic forces."""
        delta_time = global_clock.getDt()
        self.accumulator += delta_time
        updated = False
        #print self.accumulator, delta_time
        while self.accumulator > self.step_size:
            self.accumulator -= self.step_size
            updated = True
            
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
            
            self.ode_body.addForce(linear_force)

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

            self.ode_body.addRelTorque(elevator_af + ailerons_af + rudder_af +
                                     roll_damping_avf + pitch_damping_avf + yaw_damping_avf)

            # Forces to rotate the forward vector towards the velocity vector
            # and vice versa
            fvv_torque, fvv_force = self._forwardAndVelocityVectorForces(up,right,norm_v,speed)
            self.ode_body.addRelTorque(fvv_torque)
            self.ode_body.addForce(fvv_force)

            if position.getZ() < 0:
                position.setZ(0)
                velocity.setZ(0)
                self.setPosition(position)
                self.setVelocity(velocity)
            self.rudder = 0.0
            self.elevator = 0.0
            self.ailerons = 0.0
            self.world.quickStep(self.step_size)
        if updated:
            self.node.setPosQuat(render, self.position(), quat)
        return task.cont

    def destroy():
        """Call this while deactivating physics on a plane."""
        # TODO: clean up stuff
        pass
