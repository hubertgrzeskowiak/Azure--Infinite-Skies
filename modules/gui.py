"""Module containing graphical user interface objects"""

from math import degrees, radians, pi, tan,sin,cos

from direct.gui.DirectGui import OnscreenText
from direct.showbase.ShowBase import Point3, Point2, Vec3, Vec4
from pandac.PandaModules import TextNode
from pandac.PandaModules import GeomVertexFormat,GeomVertexData,GeomTriangles
from pandac.PandaModules import Geom,GeomNode,GeomVertexWriter,GeomLines

from views import DETACHED

VELOCITY_INDICATOR = '<>'
CENTRE_AXIS = '[_]'
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
    def createOnscreenText(self,pos=(0.0,0.0),align=TextNode.ACenter,
                        colour=None):
        if colour is None:
            colour = self.colour
        return OnscreenText(style=1,fg=colour,pos=pos,align=align,scale=0.05)
    
    def createPitchLine(self,colour=None):
        if colour is None:
            colour = self.colour
        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices",format,Geom.UHStatic)
        
        vertexWriter=GeomVertexWriter(vdata,"vertex")
        vertexWriter.addData3f(0.5,0.0,0.0)
        vertexWriter.addData3f(0.25,0.0,0.0)
        vertexWriter.addData3f(-0.25,0.0,0.0)
        vertexWriter.addData3f(-0.5,0.0,0.0)
        
        line = GeomLines(Geom.UHStatic)
        line.addVertices(0,1)
        line.closePrimitive()
        line2 = GeomLines(Geom.UHStatic)
        line2.addVertices(2,3)
        line2.closePrimitive()
        
        lineGeom = Geom(vdata)
        lineGeom.addPrimitive(line)
        lineGeom.addPrimitive(line2)
        
        lineGN=GeomNode("splitline")
        lineGN.addGeom(lineGeom)
        lineNP = aspect2d.attachNewNode(lineGN)
        return lineNP
            
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
        
        
        self.centre_axis = self.createOnscreenText((0.0, 0.0))
        self.centre_axis.setText(CENTRE_AXIS)
        self.velocity_indicator = self.createOnscreenText((0.0, 0.0))
        self.velocity_indicator.setText(VELOCITY_INDICATOR)
        
        # Pitch lines
        self.pitchlines = {}
        self.pitchnumbersL = {}
        self.pitchnumbersR = {}
        for angle in range(0,179,PITCH_STEP):
            if angle > 90: 
                angletext = angle - 180
            else:
                angletext = angle
            self.pitchlines[angle] = self.createPitchLine()
            self.pitchnumbersL[angle] = self.createText(str(angletext))
            self.pitchnumbersL[angle][1].reparentTo(self.pitchlines[angle])
            self.pitchnumbersR[angle] = self.createText(str(angletext))
            self.pitchnumbersR[angle][1].reparentTo(self.pitchlines[angle])
    
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
        
        self.centre_axis.setPos(centre_axis.getX(),centre_axis.getY())
    
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
        
        self.velocity_indicator.setPos(velocity_axis.getX(),velocity_axis.getY())
            
        levelforward = node.getQuat().getForward() * 1.0
        levelforward.setZ(0.0)
        levelforward.normalize()
        
        roll = node.getR()
        for angle,line in self.pitchlines.iteritems():
            pitchedline = levelforward + Vec3(0.0,0.0,tan(radians(angle)))
            pitchedline.normalize()
            pitched_axis = self.getScreenPoint(pitchedline)
            line.setR(-roll)
            line.setPos(pitched_axis.getX(),0.0,pitched_axis.getY())
            self.pitchnumbersL[angle][1].setR(roll)
            self.pitchnumbersL[angle][1].setPos(-0.6,0.0,0)
            self.pitchnumbersR[angle][1].setR(roll)
            self.pitchnumbersR[angle][1].setPos(0.6,0.0,0)
            #self.pitchnumbersR[angle][1].setR(-roll)
        
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
