""" this module provides the flight physics for the aircraft """

# Trig and angle functions
from math import radians, pi
# Math functions
from math import sqrt

from direct.showbase.ShowBase import Vec3

from modules.utils import ListInterpolator


PI_OVER_2 = pi/2.0

DEF_DYN = {"p":Vec3(0.0,0.0,0.0),
           "v":Vec3(0.0,0.0,0.0),
           "a":Vec3(0.0,0.0,0.0),
           "m":1000.0,
           "fw":Vec3(0.0,1.0,0.0),
           "up":Vec3(0.0,0.0,1.0),
           "ri":Vec3(1.0,0.0,0.0),
           "ang_p":Vec3(0.0,0.0,0.0),
           "ang_v":Vec3(0.0,0.0,0.0),
           "ang_a":Vec3(0.0,0.0,0.0),
           "moments":Vec3(1.0,1.0,1.0),
           "alpha":0.0,
           "alpha_v":0.0,
           "beta":0.0,
           "beta_v":0.0,
           "thrust_perc":0.0,
           "controls":Vec3(0.0,0.0,0.0), # elevator, ailerons, rudder
          }

DEF_SPECS = {"unloaded_mass":4000.0,
             "max_speed":600.0,
             "roll_speed":15.0,
             "pitch_speed":10.0,
             "yaw_speed":5.0,
             "wing_area":48.0,
             "wing_span":24.0,
             "wing_chord":2.0,
             "aspect_ratio":12.0,
             "drag_coefs":[0.9,0.1,0.9],
             "drag_areas":[30.0,2.75,50.0],
             "lift_vs_alpha":ListInterpolator([[radians(-18.0),-1.05],
                                           [radians(-15.0),-1.75],
                                           [radians(15.0),1.75],
                                           [radians(18.0),1.05]],
                                           0.0,0.0),
             "sf_vs_beta":ListInterpolator([[radians(-18.0),-2.05],
                                           [radians(-15.0),-1.75],
                                           [radians(15.0),1.75],
                                           [radians(18.0),2.05]],
                                           0.0,0.0),
             "max_thrust":5000.0,
             
             #----------------------------------------------
             # New linear forces specs
             #----------------------------------------------
             "lift_coef_0":0.28, # Lift at zero alpha (CL0)
             "drag_coef_0":0.03, # Drag at zero alpha (CD0)
             "lift_coef_alpha":3.45, # Lift gradient (CLalpha)
             "drag_coef_alpha":0.3, # Drag gradient (CDalpha)
             
             "lift_coef_pitch_rate": 0.0,
             "lift_coef_alpha_rate": 0.72,
             
             "side_force_beta":-0.98, # side force from beta
             
             #----------------------------------------------
             # Control effects on linear forces
             #----------------------------------------------
             "lift_elevator":0.36,      # lift from elevator
             "drag_elevator":0.1,      # drag from elevator
             "side_force_rudder":0.1,     # side force from rudder
             
             #----------------------------------------------
             # basic control rotation effects
             #----------------------------------------------
             "pitch_elevator": 1.0,
             "roll_ailerons": 1.0,
             "yaw_rudder": 1.0,
             
             #----------------------------------------------
             # control cross terms
             #----------------------------------------------
             "pitch_ailerons": 0.0,
             "pitch_rudder": 0.0,
             "roll_elevator": 0.0,
             "roll_rudder": 0.0,
             "yaw_elevator": 0.0,
             "yaw_ailerons": 0.0,
             
             #----------------------------------------------
             # basic damping forces
             #----------------------------------------------
             "pitch_damping": -0.05,
             "roll_damping": -0.05,
             "yaw_damping": -0.05,
             
             #----------------------------------------------
             # deviation from flight path (alpha & beta)
             #----------------------------------------------
             "pitch_alpha_0": 0.0,
             "pitch_alpha": 0.0,
             "pitch_beta": 0.0,
             "roll_alpha": 0.0,
             "roll_beta": 0.0,
             "yaw_alpha": 0.0,
             "yaw_beta": 0.0,
             
             #----------------------------------------------
             # cross rotation rate effects
             #----------------------------------------------
             "pitch_roll_rate": 0.0,
             "pitch_yaw_rate": 0.0,
             "roll_pitch_rate": 0.0,
             "roll_yaw_rate": 0.0,
             "yaw_pitch_rate": 0.0,
             "yaw_roll_rate": 0.0,
             
             #----------------------------------------------
             # inertias
             #----------------------------------------------
             "roll_inertia":  8090.0,
             "pitch_inertia": 25900.0,
             "yaw_inertia": 29200.0,
             "roll_yaw_inertia_mix":1300.0,
             
             #----------------------------------------------
             # Control specifications
             #----------------------------------------------
             #"max_control":[0.5236,0.5326,0.2618],
             "max_control":[0.05236,0.05326,0.02618],
             "control_application_rate": [1.0,1.0,1.0],
             "control_return_rate": [1.0,1.0,1.0],
             }

class DynamicVariables(object):
    """ class to simplify passing around the dynamic variables """
    
    # give the derived class a chance to change the default set of
    #    dynamic variables
    def_dyn = DEF_DYN
    def_specs = DEF_SPECS
    
    def __init__(self,**kw):
        """ initialisation - see loadVariables for argument handling """
        self.loadVariables(**kw)
    
    def loadVariables(self,**kw):
        """ Variable loading:
        Variables can be passed as a dictionary or in a keyword=value form.
        Unknown keywords are currently ignored.
        Missing keywords all have default values.
        """
        for var in self.def_dyn.keys():
            try:
                setattr(self,var,kw[var])
            except:
                #print "Warning: variable %s not specified." % var,
                try:
                    v = getattr(self,var)
                    #print "Previous value kept." 
                except:
                    setattr(self,var,self.def_dyn[var])
                    #print "Using default value."
    
    def loadFromPandaNode(self,node):
        """ use a panda node to set positions, angles and direction vectors """
        self.p = node.getPos()
        
        quat = node.getQuat()
        self.fw = quat.getForward()
        self.up = quat.getUp()
        self.ri = quat.getRight()
        
        self.ang_p[0] = node.getP()
        self.ang_p[1] = node.getR()
        self.ang_p[2] = node.getH()
    
    def exportToPandaNode(self,node,dt):
        """ update a panda node with the current position and angles """
        node.setPos(self.p)
        node.setP(node,self.ang_v[0]*dt)
        node.setR(node,self.ang_v[1]*dt)
        node.setH(node,self.ang_v[2]*dt)
    
    def calcDerivedValues(self):
        """ pre-calculate useful information for dynamics calculations """
        v = self.v
        self.v_sq = v.lengthSquared()
        self.v_norm = v + v.zero()
        self.v_norm.normalize()
        
        self.alpha = self.v_norm.angleRad(self.up) - PI_OVER_2
        self.beta = self.v_norm.angleRad(self.ri) - PI_OVER_2
        self.speed = sqrt(self.v_sq)
        self.altitude = self.p.getZ()
        
        # need to add in rotations of the thrust to correct the vector
        self.thrust_vector = self.fw + v.zero()
    
    def getPVA(self):
        """ return the current position, velocity and acceleration vectors """
        return self.p,self.v,self.a
    
    def getAngularPVA(self):
        """ return the current angular positions, velocities and accelerations
        as vectors """
        return self.ang_p,self.ang_v,self.ang_a
        
    def setPVA(self,p,v,a):
        """ set the new position, velocity and acceleration vectors """
        self.p = p
        self.v = v
        self.a = a
    def setAngularPVA(self,p,v,a):
        """ set the new angular positions, velocities and accelerations """
        self.ang_p = p
        self.ang_v = v
        self.ang_a = a

class BaseFDM(object):
    def_specs = DEF_SPECS
    
    def __init__(self,**kw):
        """ Initialisation. For information on arguments, see loadSpecs or
        DynamicVariables.loadVariables
        """
        self.loadSpecs(**kw)
        self.dyn_vars = DynamicVariables()
        self.loadDynamicVariables(**kw)
    
    def loadSpecs(self,**kw):
        """ Specification loading:
        Specs can be passed as a dictionary or in a keyword=value form.
        Unknown keywords are currently ignored.
        Missing keywords all have default values.
        """
        for spec in self.def_specs.keys():
            try:
                setattr(self,spec,kw[spec])
            except:
                #print "Warning: spec %s not specified." % spec,
                try:
                    s = getattr(self,spec)
                    #print "Previous value kept." 
                except:
                    setattr(self,spec,self.def_specs[spec])
                    #print "Using default value."
    
    def loadDynamicVariables(self,**kw):
        """ loads dynamic variabls - see DynamicVariables.loadVariables """
        self.dyn_vars.loadVariables(**kw)
    
    def resetCalculationConstants(self):
        """ reset calculation constants """
        pass
    
    #-----------------------------------------
    # Integration methods
    #-----------------------------------------
    def eulerInt(self,dynvars,p,v,a,accelf,dt):
        """ Euler integration """
        new_a = accelf(dynvars)
        new_p = p + v * dt
        new_v = v + new_a * dt
        return new_p,new_v,new_a
    
    def eulerCromerInt(self,dynvars,p,v,a,accelf,dt):
        """ Euler Cromer Integration """
        new_a = accelf(dynvars)
        new_v = v + new_a * dt
        new_p = p + new_v * dt
        return new_p,new_v,new_a
        
    def velocityVerletInt(self,dynvars,p,v,a,accelf,dt):
        """ Velocity Verlet Integration """
        new_p = p + v*dt + a*dt*dt*0.5
        new_a = accelf(dynvars)
        new_v = v + (a + new_acc)*dt*0.5
        return new_p,new_v,new_a
    
    def modVelocityVerletInt(self,dynvars,p,v,a,accelf,dt):
        """ Modified Velocity Verlet Integration """
        new_p = p + v*dt + a*dt*dt*0.5
        new_v = v + a*dt*0.5
        new_a = accelf(dynvars)
        new_v = new_v + new_a*dt*0.5
        return new_p,new_v,new_a
    
    def centreControl(self,which,dt):
        """ Control centering for keyboard controls """
        deflection = self.dyn_vars.controls[which]
        rate = self.control_return_rate[which]
        
        if deflection != 0.0:
            change = abs(rate*dt)
            
            if abs(deflection) < change:
                deflection = 0.0
            elif deflection < 0.0:
                deflection += change
            else:
                deflection -= change
            self.dyn_vars.controls[which] = deflection
    
    def applyControl(self,which,direction,dt):
        """ Control appliction for keyboard controls """
        deflection = self.dyn_vars.controls[which]
        max_deflection = self.max_control[which]
        rate = self.control_application_rate[which]*direction
        
        change = rate*dt
        
        if abs(deflection + change) >= max_deflection:
            if deflection < 0.0:
                deflection = -max_deflection
            else:
                deflection = max_deflection
        else:
            deflection += change
        self.dyn_vars.controls[which] = deflection
    
    def linearA(self,dynvars):
        """ linear acceleration function - to be overridden """
        return dynvars.a
    
    def rotationalA(self,dynvars):
        """ rotational acceleration function - to be overridden """
        return dynvars.ang_a

class FlightDynamicsModel(BaseFDM):
    
    def resetCalculationConstants(self):
        """pre-calculate some calculation constants from the
        flight parameters"""
        half_rho = 0.602
        self.lift_factor = half_rho * self.wing_area
        
        # could modify lift_induced_drag by a factor of 1.05 to 1.15
        self.lift_induced_drag_factor = (-1.0) * self.lift_factor / \
                                        (pi*self.aspect_ratio)
        
        self.drag_factor_x = (-1.0) * half_rho * self.drag_areas[0] * \
                                                 self.drag_coefs[0]
        self.drag_factor_y = (-1.0) * half_rho * self.drag_areas[1] * \
                                                 self.drag_coefs[1]
        self.drag_factor_z = (-1.0) * half_rho * self.drag_areas[2] * \
                                                 self.drag_coefs[2]
        self.gravity = Vec3(0.0,0.0,(-9.81) * self.dyn_vars.m)
    
    def lift(self,dynvars):
        """return the lift force vector generated by the wings"""
        # lift direction is always perpendicular to the airflow
        lift_vector = dynvars.ri.cross(dynvars.v_norm)
        return lift_vector * dynvars.v_sq * self.lift_factor * \
                             self.lift_vs_alpha[dynvars.alpha]
    
    def profileDrag(self,dynvars):
        """ calculate the profile drag """
        v = dynvars.v
        speed_x = dynvars.ri.dot(v)
        speed_y = dynvars.fw.dot(v)
        speed_z = dynvars.up.dot(v)
        
        drag_x = dynvars.ri*speed_x*speed_x*self.drag_factor_x
        drag_y = dynvars.fw*speed_y*speed_y*self.drag_factor_y
        drag_z = dynvars.up*speed_z*speed_z*self.drag_factor_z
        if speed_x < 0.0:
            drag_x = -drag_x
        if speed_y < 0.0:
            drag_y = -drag_y
        if speed_z < 0.0:
            drag_z = -drag_z
        return drag_x + drag_y + drag_z
    
    def inducedDrag(self,dynvars):
        """ get the induced drag coefficient """
        # Cdi = (Cl*Cl)/(pi*AR*e)
        lift_coef = self.lift_vs_alpha[dynvars.alpha]
        ind_drag_coef = lift_coef * lift_coef / (pi * self.aspect_ratio * 1.10)
        # and calculate the drag induced by the creation of lift
        return -dynvars.v * sqrt(dynvars.v_sq) * self.lift_factor * \
                                                 ind_drag_coef
   
    def sideDrag(self,dynvars):
        """return the side force vector from the beta angle"""
        return dynvars.ri * self.sf_vs_beta[dynvars.beta] * dynvars.v_sq
    
    def thrust(self,dynvars):
        """return the force vector produced by the aircraft engines"""
        return dynvars.thrust_vector * dynvars.thrust_perc * self.max_thrust
    
    def linearA(self,dynvars):
        """calculate the forces due to the velocity and orientation of the aircraft"""
        
        dynvars.calcDerivedValues()
        lift = self.lift(dynvars)
        profile_drag = self.profileDrag(dynvars)
        induced_drag = self.inducedDrag(dynvars)
        side_drag = self.sideDrag(dynvars)
        thrust = self.thrust(dynvars)
        force = lift + profile_drag + induced_drag + side_drag + self.gravity + thrust
        
        # if the plane is on the ground, the ground reacts to the downward force
        # TODO (gjmm): need to modify in order to consider reaction to objects
        #              at different altitudes.
        if dynvars.altitude == 0.0 and force[2] < 0.0:
            force.setZ(0.0)
        return force/dynvars.m

class RotationalFlightDynamicsModel(FlightDynamicsModel):
    """ flight dynamics model adding physics of control surfaces """
    
    def rotationFromControls(self,dynvars):
        """ returns a rotational acceleration associated directly with the
        control surfaces """
        b = self.wing_span
        c = self.wing_chord
        half_b = b/2.0
        half_c = c/2.0
        v = dynvars.speed
        v_sq = dynvars.v_sq
        
        #----------------------------------------------
        # basic control rotation effects
        #----------------------------------------------
        pitch_elevator = self.pitch_elevator * dynvars.controls[0]
        roll_ailerons = self.roll_ailerons * dynvars.controls[1]
        yaw_rudder = self.yaw_rudder*dynvars.controls[2]
        
        #----------------------------------------------
        # control cross terms
        #----------------------------------------------
        pitch_ailerons = self.pitch_ailerons * dynvars.controls[1]
        pitch_rudder = self.pitch_rudder * dynvars.controls[2]
        roll_elevator = self.roll_elevator * dynvars.controls[0]
        roll_rudder = self.roll_rudder * dynvars.controls[2]
        yaw_elevator = self.yaw_elevator * dynvars.controls[0]
        yaw_ailerons = self.yaw_ailerons*dynvars.controls[1]
        
        pitch = (pitch_elevator+pitch_ailerons+pitch_rudder)*half_c
        roll = (roll_elevator+roll_ailerons+roll_rudder)*half_b
        yaw = (yaw_elevator+yaw_ailerons+yaw_rudder)*half_b
        
        return Vec3(pitch,roll,yaw)*self.lift_factor*v
    
    def rotationDamping(self,dynvars):
        """ rotational damping forces """
        alpha = dynvars.alpha
        beta = dynvars.beta
        b = self.wing_span
        half_b = b/2.0
        c = self.wing_chord
        half_c = c/2.0
        v = dynvars.speed
        
        pitch_damping = self.pitch_damping*dynvars.ang_v[0]*half_c
        roll_damping = self.roll_damping*dynvars.ang_v[1]*half_b
        yaw_damping = self.yaw_damping*dynvars.ang_v[2]*half_b
        
        return Vec3(pitch_damping,roll_damping,yaw_damping)*self.lift_factor # *v
    
    def rotationFromPathDeviation(self,dynvars):
        alpha = dynvars.alpha
        c = self.wing_chord
        half_c = c/2.0
        beta = dynvars.beta
        b = self.wing_span
        half_b = b/2.0
        v = dynvars.speed
        
        
        pitch_alpha = (self.pitch_alpha_0 + self.pitch_alpha*alpha)*c
        # dihedral effect
        roll_beta = self.roll_beta * beta * b
        # weather cocking
        yaw_beta = self.yaw_beta * beta * b
        
        return Vec3(pitch_alpha,roll_beta,yaw_beta)*self.lift_factor*v
    
    def rotSecondaryEffects(self,dynvars):
        """ further effects on the rotational accelerations """
        alpha = dynvars.alpha
        c = self.wing_chord
        half_c = c/2.0
        beta = dynvars.beta
        b = self.wing_span
        half_b = b/2.0
        v = dynvars.speed
        
        pitch_alpha = (self.pitch_m_0 + self.pitch_m_a * alpha) * \
               self.lift_factor * c * v
        dihedral_effect = self.de_beta * beta * \
               self.lift_factor * b * v
        weather_cocking = self.wc_beta * beta * \
               self.lift_factor * b * v
        rudder_adverse_yaw = self.rudder_ay * dynvars.controls[1]*\
               self.lift_factor*half_b*v
        return Vec3(pitch_alpha,dihedral_effect,weather_cocking+rudder_adverse_yaw)
        
    def rotationalA(self,dynvars):
        """ add a method for rotational dynamics """
        dynvars.calcDerivedValues()
        
        control = self.rotationFromControls(dynvars)
        damping = self.rotationDamping(dynvars)
        path_deviation = self.rotationFromPathDeviation(dynvars)
        
        return control + damping + path_deviation
        
