"""Module containing graphical user interface objects"""

from math import degrees, radians, pi

from direct.gui.DirectGui import OnscreenText
from direct.showbase.ShowBase import Point3, Point2, Vec3
from pandac.PandaModules import TextNode

from views import DETACHED

VELOCITY_INDICATOR = '<>'
CENTRE_AXIS = '[_]'

def printInstructions(instructions = ""):
    """Give me some text and i'll print it at the top left corner"""
    # temporary function. used until we have some real interface
    OnscreenText(
        text = instructions,
        style = 1,
        fg = (1,1,1,1),
        pos = (-1.3, 0.95),
        align = TextNode.ALeft,
        scale = .05)

class HUD(object):
    def __init__(self,model,cam):
        self.model = model
        self.camera = cam
        self.heading_text = OnscreenText(text="head: ",style=1,fg=(1,1,1,1),
                                     pos=(0.0, 0.95),align=TextNode.ACenter,
                                     scale=0.05)
        self.altitude_text = OnscreenText(text="alt: ",style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.velocity_text = OnscreenText(text="vel: ",style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.85),align=TextNode.ALeft,
                                     scale=0.05)
        self.gforce_text = OnscreenText(text="G: ",style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.75),align=TextNode.ALeft,
                                     scale=0.05)
        self.axialgforce_text = OnscreenText(text="axial G: ",style=1,
                                     fg=(1,1,1,1),pos=(1.0, 0.65),
                                     align=TextNode.ALeft,scale=0.05)
        self.lateralgforce_text = OnscreenText(text="lateral G: ",style=1,
                                     fg=(1,1,1,1),pos=(1.0, 0.55),
                                     align=TextNode.ALeft,scale=0.05)
        self.centre_axis = OnscreenText(text=CENTRE_AXIS,style=1,fg=(1,1,1,1),
                                     pos=(0.0, 0.0),align=TextNode.ACenter,
                                     scale=0.1)
        self.velocity_indicator = OnscreenText(text=VELOCITY_INDICATOR,style=1,
                                     fg=(1,1,1,1),pos=(0.0, 0.0),
                                     align=TextNode.ACenter,scale=0.05)
        
    def update(self):
        # need to know the field of view
        fov = base.cam.node().getLens().getFov()
        
        # stuff to work out the direction to point the HUD velocity graphic
        # collect the vectors:
        v_norm = self.model.velocity * 1.0
        v_norm.normalize()
        model_right = self.model.node().getQuat().getRight()
        model_up = self.model.node().getQuat().getUp()
        
        # calculate the horizontal and vertical angles
        v_angle_hor = v_norm.angleRad(model_right) - pi/2.0
        v_angle_ver = v_norm.angleRad(model_up) - pi/2.0
        
        # we also need to know where the axis is going to reside
        if self.camera.getViewMode() == DETACHED:
            # in this case we should avoid any offsetting
            centre_axis_offset = 0.0
        else:
            # now need to work out where the camera is pointing
            # it seems that the forward vector for the camera is constant
            #       in all the cases apart from DETACHED mode
            cam_forward = self.camera.camera.getQuat().getForward()
            #       and so our up vector also has to be constant..
            up = Vec3(0.0,0.0,1.0)
            
            # finally we can get the angle
            axial_angle = cam_forward.angleRad(up) - pi/2.0

            # and we can move the axis in ratio to the field of view
            # the factor of 2.0 is on purpose as the fov is twice the angle
            #       between the centre and the edge of the screen
            centre_axis_offset = 2.0*axial_angle/radians(fov[1])
        
        # at this point we can set the centre point
        self.centre_axis.destroy()
        self.centre_axis = OnscreenText(text=CENTRE_AXIS,style=1,fg=(1,1,1,1),
                                 pos=(0.0, centre_axis_offset),
                                 align=TextNode.ACenter,scale=0.05)
        
        # and we can also finish off working out the position of the 
        #       velocity indicator
        velocity_offset0 = -2.0*v_angle_hor/radians(fov[0])
        velocity_offset1 = centre_axis_offset - 2.0*v_angle_ver/radians(fov[1])
        
        self.velocity_indicator.destroy()
        self.velocity_indicator = OnscreenText(text=VELOCITY_INDICATOR,style=1,
                                     fg=(1,1,1,1),
                                     pos=(velocity_offset0,velocity_offset1),
                                     align=TextNode.ACenter,scale=0.05)
        
        heading = - self.model.node().getH()
        if heading < 0.0:
            heading += 360.0
        if heading >= 359.95: heading = 0.0
        
        head = '%.1f' %abs(round(heading,1))
        alt = 'alt: %d' %int(self.model.node().getZ())
        #1 m/s = 3.6 km/h
        vel = 'vel: %d' %int(self.model.speed()*3.6)
        g = 'G: %.1f' %round(self.model.gForce(),1)
        ag = 'axial G: %.1f' %round(self.model.axialG(),1)
        lg = 'lateral G: %.1f' %round(self.model.lateralG(),1)
        
        self.heading_text.destroy()
        self.altitude_text.destroy()
        self.velocity_text.destroy()
        self.gforce_text.destroy()
        self.axialgforce_text.destroy()
        self.lateralgforce_text.destroy()
        self.heading_text = OnscreenText(text=head,style=1,fg=(1,1,1,1),
                                     pos=(0.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.altitude_text = OnscreenText(text=alt,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.velocity_text = OnscreenText(text=vel,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.85),align=TextNode.ALeft,
                                     scale=0.05)
        self.gforce_text = OnscreenText(text=g,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.75),align=TextNode.ALeft,
                                     scale=0.05)
        self.axialgforce_text = OnscreenText(text=ag,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.65),align=TextNode.ALeft,
                                     scale=0.05)
        self.lateralgforce_text = OnscreenText(text=lg,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.55),align=TextNode.ALeft,
                                     scale=0.05)
