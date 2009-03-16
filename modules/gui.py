"""Module containing graphical user interface objects"""

from math import degrees, radians, pi, tan, sin, cos

from direct.showbase.ShowBase import Point3, Point2, Vec3
from pandac.PandaModules import GeomVertexFormat,GeomVertexData
from pandac.PandaModules import Geom,GeomNode,GeomVertexWriter,GeomLines
from direct.gui.DirectGui import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import TextNode

from views import DETACHED

PITCH_STEP = 10
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
    """ Head Up Display """
    def __init__(self,model,cam,colour=(1,1,1,1)):
        """ HUD initialisation """
        
        self.model = model
        self.camera = cam
        
        self.colour = colour
        self.default_element_scale = 0.05
        self.heading_text = self.createOnscreenText((0.0, 0.95))
        self.altitude_text = self.createOnscreenText((1.0, 0.95),
                                    align=TextNode.ALeft)
        self.velocity_text = self.createOnscreenText((1.0, 0.85),
                                    align=TextNode.ALeft)
        self.gforce_text = self.createOnscreenText((1.0, 0.75),
                                    align=TextNode.ALeft)
        self.axialgforce_text = self.createOnscreenText((1.0, 0.65),
                                    align=TextNode.ALeft)
        self.lateralgforce_text = self.createOnscreenText((1.0, 0.55),
                                    align=TextNode.ALeft)
        
        self.centre_axis = self.createCentreMark()
        #self.velocity_indicator = self.createOnscreenText((0.0, 0.0))
        #self.velocity_indicator.setText(VELOCITY_INDICATOR)
        self.velocity_indicator = OnscreenImage(image='velocityindicator.png',
                                    pos = (0.0,0.0,0.0),scale=0.05)
        self.velocity_indicator.reparentTo(aspect2d)
        # Pitch lines and numbers
        self.pitchlines = {}
        self.pitchnumbersL = {}
        self.pitchnumbersR = {}
        
        for angle in range(0,179,PITCH_STEP):
            if angle > 90: 
                angletext = angle - 180
            else:
                angletext = angle
            
            # create a line
            self.pitchlines[angle] = self.createPitchLine()
            
            # and create two numbers to display either side of the pitch line
            self.pitchnumbersL[angle] = self.createText(str(angletext))
            self.pitchnumbersR[angle] = self.createText(str(angletext))
            
            # reparent to the previously created pitchline so that the position
            #       and orientation is described relative to the pitchline
            self.pitchnumbersL[angle][1].reparentTo(self.pitchlines[angle])
            self.pitchnumbersR[angle][1].reparentTo(self.pitchlines[angle])

    
    def getScreenPoint(self,vector):
        """ get the point on screen representing centre axis """
        
        # need the node of the airplane in order to determine position
        #       and forward direction
        node = self.model.node()
        target_point = Point3(node.getPos() + vector * 10000)
        
        # in order to convert the target_point to the screen position
        #       need to convert the coordinates to the top level node
        world_node = node.getTop()
        converted_point = base.cam.getRelativePoint(world_node,target_point)
        
        # create a point to store the result in and project the point
        #       onto the lens
        returned_point = Point2(0.0,0.0)
        base.cam.node().getLens().project(converted_point,returned_point)
        
        return returned_point
    
    def staticElementUpdate(self):
        """ update static parts of the HUD display """
        
        if self.camera.getViewMode() == DETACHED:
            centre_axis = Point2(0.0,0.0)
        else:            
            node = self.model.node()
            forward = node.getQuat().getForward()
            centre_axis = self.getScreenPoint(forward)
        self.centre_axis.setPos(centre_axis.getX(),0.0,centre_axis.getY())
    
    def update(self):
        """ update the HUD display """
        
        # TODO (gjmm): any static enements should only change when the camera
        #               type changes so move this to save work
        self.staticElementUpdate()
        
        node = self.model.node()
        
        #if self.camera.getViewMode() == DETACHED:
        #    # TODO (gjmm): work out meaningful alternatives for views where
        #    #               things like the velocity indicator don't work
        #    #               in projected coordinates
        
        v_norm = self.model.velocity * 1.0
        v_norm.normalize()
        velocity_axis = self.getScreenPoint(v_norm)
        
        self.velocity_indicator.setPos(velocity_axis.getX(),0.0,velocity_axis.getY())
        self.velocity_indicator.setTransparency(TransparencyAttrib.MAlpha)

        levelforward = node.getQuat().getForward() * 1.0
        levelforward.setZ(0.0)
        levelforward.normalize()
        
        roll = node.getR()
        for angle,line in self.pitchlines.iteritems():
            # adding a vector with the tan of the angle rotates the normalised
            #       level vector to that angle
            pitchedline = levelforward + Vec3(0.0,0.0,tan(radians(angle)))
            pitchedline.normalize()
            # calculate the appropriate screen position for this vector
            pitched_axis = self.getScreenPoint(pitchedline)
            
            # now roll the line so that it is level with the horizon
            line.setR(-roll)
            # and move to the calculated position
            line.setPos(pitched_axis.getX(),0.0,pitched_axis.getY())
            
            # finally we modify the numbers associated with the lines..
            # the following transformations are specified relative to the lines
            
            # line rotation caused the numbers to rotate so we'll rotate back
            self.pitchnumbersL[angle][1].setR(roll)
            self.pitchnumbersR[angle][1].setR(roll)
            # and now move them along to either side of the lines
            self.pitchnumbersL[angle][1].setPos(-0.6,0.0,0)
            self.pitchnumbersR[angle][1].setPos(0.6,0.0,0)
        
        heading = - node.getH()
        if heading < 0.0:
            heading += 360.0
        if heading >= 359.95: heading = 0.0
        
        head = '%.1f' %abs(round(heading,1))
        alt = 'alt: %d' %int(node.getZ())
        #1 m/s = 3.6 km/h
        vel = 'vel: %d' %int(self.model.speed()*3.6)
        g = 'G: %.1f' %round(self.model.gForce(),1)
        ag = 'axial G: %.1f' %round(self.model.axialG(),1)
        lg = 'lateral G: %.1f' %round(self.model.lateralG(),1)
        
        self.heading_text.setText(head)
        self.altitude_text.setText(alt)
        self.velocity_text.setText(vel)
        self.gforce_text.setText(g)
        self.axialgforce_text.setText(ag)
        self.lateralgforce_text.setText(lg)
    
    
    def createOnscreenText(self,pos=(0.0,0.0),align=TextNode.ACenter,
                        colour=None):
        """ slight simplification of OnscreenText object creation """
        if colour is None:
            colour = self.colour
        return OnscreenText(style=1,fg=colour,pos=pos,align=align,scale=0.05)
    
    def createText(self,text,pos=(0.0,0.0),align=TextNode.ACenter,
                    scale=None,colour=None):
        if colour is None:
            colour = self.colour
        if scale is None:
            scale = self.default_element_scale
        
        text_node = TextNode('text')
        text_node.setText(text)
        text_node.setGlyphScale(scale)
        text_node.setAlign(align)
        text_node.setTextColor(colour[0],colour[1],colour[2],colour[3])
        generated_text = text_node.generate()
        text_node_path = render2d.attachNewNode(generated_text)
        text_node_path.setPos(pos[0],0.0,pos[1])
        return text_node,text_node_path
        
    def createPitchLine(self,colour=None):
        """ create a line to hint at the pitch of the aircraft on the hud """
        if colour is None:
            colour = self.colour
        
        # These lines are drawn from scratch rather than using a graphic file
        
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices",format,Geom.UHStatic)
        
        # create vertices to add to use in creating lines
        vertexWriter=GeomVertexWriter(vdata,"vertex")
        # here we define enough positions to create two separated lines
        vertexWriter.addData3f(0.5,0.0,0.0)
        vertexWriter.addData3f(0.25,0.0,0.0)
        vertexWriter.addData3f(-0.25,0.0,0.0)
        vertexWriter.addData3f(-0.5,0.0,0.0)
        
        # create the primitives
        line = GeomLines(Geom.UHStatic)
        line.addVertices(0,1)
        line.closePrimitive()
        line2 = GeomLines(Geom.UHStatic)
        line2.addVertices(2,3)
        line2.closePrimitive()
        
        # add the lines to a geom object
        lineGeom = Geom(vdata)
        lineGeom.addPrimitive(line)
        lineGeom.addPrimitive(line2)
        
        # create the node..
        lineGN=GeomNode("splitline")
        lineGN.addGeom(lineGeom)
        
        # and parent the node to aspect2d
        lineNP = aspect2d.attachNewNode(lineGN)
        return lineNP
    
    def createCentreMark(self,colour=None):
        """ create a line to hint at the pitch of the aircraft on the hud """
        if colour is None:
            colour = self.colour
        
        # These lines are drawn from scratch rather than using a graphic file
        
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices",format,Geom.UHStatic)
        
        # create vertices to add to use in creating lines
        vertexWriter=GeomVertexWriter(vdata,"vertex")
        # essentially I am trying to create a line that gives an idea of
        #       where the forward vector of the plane is pointing which
        #       helps indicate the pitch
        # the bends in the line could be used to indicate a few angles but
        #       I am not sure how useful this really is.
        vertexWriter.addData3f(0.15,0.0,0.0)
        vertexWriter.addData3f(0.10,0.0,0.0)
        vertexWriter.addData3f(0.05,0.0,-0.025)
        vertexWriter.addData3f(0.00,0.0,0.025)
        vertexWriter.addData3f(-0.05,0.0,-0.025)
        vertexWriter.addData3f(-0.10,0.0,0.0)
        vertexWriter.addData3f(-0.15,0.0,0.0)
        
        # create the primitives
        line = GeomLines(Geom.UHStatic)
        line.addVertices(0,1)
        line.addVertices(1,2)
        line.addVertices(2,3)
        line.addVertices(3,4)
        line.addVertices(4,5)
        line.addVertices(5,6)
        line.closePrimitive()
        
        # add the lines to a geom object
        lineGeom = Geom(vdata)
        lineGeom.addPrimitive(line)
        
        # create the node..
        lineGN=GeomNode("centremark")
        lineGN.addGeom(lineGeom)
        
        # and parent the node to aspect2d
        lineNP = aspect2d.attachNewNode(lineGN)
        return lineNP
