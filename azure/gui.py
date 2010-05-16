# -*- coding: utf-8 -*-
"""Module containing graphical user interface objects"""

import sys
from math import degrees, radians, pi, tan, sin, cos

from pandac.PandaModules import GeomVertexFormat,GeomVertexData
from pandac.PandaModules import Geom,GeomNode,GeomVertexWriter,GeomLines
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import TextNode
from pandac.PandaModules import Point3, Point2, Vec3, Vec4
from direct.directtools.DirectGeometry import LineNodePath
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage

from views import PlaneCamera
#from core import Core

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
        self.plane_camera = PlaneCamera(base.player)
        # this font is loaded to make sure we have unicode characaters
        # specifically we want to be able to display the greek alpha character
        self.unicodefont = loader.loadFont("fonts/DejaVuSansMono.ttf")

        # keep copies of the airplane model and the camera
        self.model = model
        self.physics_node = model.node.getParent()
        self.camera = cam

        # store the requested colour to be used as default
        self.colour = colour

        self.default_element_scale = 0.05

        # many of the elements on the hud are going to be defined
        # relative to the centre axis (boresight) so create this
        self.centre_axis = self.createCentreMark()

        # altitude is going to be displayed to the right of the centre axis
        # and the climb rate is just above this
        self.altitude_text = self.createOnscreenText((0.7, 0.0),
                                    align=TextNode.ALeft,framecolour=colour)
        self.climb_text = self.createOnscreenText((0.7, 0.1),scale=0.04,
                                    align=TextNode.ALeft)

        self.altitude_text.reparentTo(self.centre_axis)
        self.climb_text.reparentTo(self.centre_axis)

        # the velocity is displayed to the left of the centre axis
        # angle of attack (alpha) and the gforce are displayed beneath
        self.velocity_text = self.createOnscreenText((-0.7, 0.0),
                                    align=TextNode.ARight,framecolour=colour)
        self.alpha_text = self.createOnscreenText((-0.7, -0.3),
                                    align=TextNode.ARight)
        self.total_gforce_text = self.createOnscreenText((-0.7, -0.4),
                                    align=TextNode.ARight)

        self.velocity_text.reparentTo(self.centre_axis)
        self.alpha_text.reparentTo(self.centre_axis)
        self.total_gforce_text.reparentTo(self.centre_axis)

        # the heading belongs centred at the top of the screen
        #       no reparenting required?
        self.heading_text = self.createOnscreenText((0.0, 0.95),
                                    align=TextNode.ACenter,framecolour=colour)

        # create and store the pitchladder lines and numbers - positioning of 
        #       these are dealt with as the HUD is updated
        lines,leftnumbers,rightnumbers = self.createPitchLadder(PITCH_STEP)
        self.pitchlines = lines
        self.pitchnumbersL = leftnumbers
        self.pitchnumbersR = rightnumbers

        # create or load graphic to indicate the current direction of motion
        self.velocity_indicator = self.createVelocityIndicator()

    def createVelocityIndicator(self,colour=None):
        """ loads an image used to represent the direction of motion """

        if colour is None:
            colour = self.colour

        # load the image, put it in aspect2d and make sure 
        #       transparency is respected
        vel_ind = OnscreenImage(image="gui/velocityindicator.png",
                                    pos = (0.0,0.0,0.0),scale=0.05,color=colour)
        vel_ind.reparentTo(aspect2d)
        vel_ind.setTransparency(TransparencyAttrib.MAlpha)
        return vel_ind

    def createPitchLadder(self,anglestep,colour=None):
        """ creates graphics in order to indicate pitch and roll """
        if colour is None:
            colour = self.colour

        # a set of dictionaries to store lines and values
        pitchlines = {}
        pitchnumbersL = {}
        pitchnumbersR = {}

        # positions used to define the x positions to start and stop the lines
        #       lines will be defined to be at y = 0, each line has a gap
        #       from 0.25 to -0.25 and the zero line is longer than the others
        zeropoints = [0.65,0.25,-0.25,-0.65]
        otherpoints = [0.5,0.25,-0.25,-0.5]

        for angletext in range(-90,90+anglestep,anglestep):
            # create a line
            if angletext == 0:
                pitchlines[angletext] = self.createPitchLine(zeropoints,
                                                                0,colour)
            elif angletext in [90,-90]:
                pitchlines[angletext] = self.createPitchLine(otherpoints,
                                                                0,colour)
            # other lines also have a line at the end at 90 degrees to the
            #       pitchlines to help indicate the direction to the horizon
            elif angletext > 0:
                pitchlines[angletext] = self.createPitchLine(otherpoints,
                                                                -0.05,colour)
            else:
                pitchlines[angletext] = self.createPitchLine(otherpoints,
                                                                0.05,colour)
            
            if angletext != 0:
                # create two numbers to display either side of the pitch line
                pitchnumbersL[angletext] = self.createText(str(angletext))
                pitchnumbersR[angletext] = self.createText(str(angletext))
                
                # reparent to the previously created pitchline so the position
                #       and orientation is described relative to the pitchline
                pitchnumbersL[angletext][1].reparentTo(pitchlines[angletext])
                pitchnumbersR[angletext][1].reparentTo(pitchlines[angletext])
        return pitchlines,pitchnumbersL,pitchnumbersR

    def getScreenPoint(self,vector):
        """ get the point on screen representing centre axis """
        # need the node of the airplane in order to determine position
        #       and forward direction
        node = self.model.node
        position = node.getPos()
        target_point = Point3(position + vector * 10000)

        # in order to convert the target_point to the screen position
        #       need to convert the coordinates to the top level node
        world_node = node.getTop()
        converted_point = base.cam.getRelativePoint(world_node,target_point)

        # create a point to store the result in and project the point
        #       onto the lens
        returned_point = Point2(0.0,0.0)
        base.cam.node().getLens().project(converted_point,returned_point)

        return returned_point

    def staticElementUpdate(self,forward):
        """ update static parts of the HUD display """
        centre_axis = self.getScreenPoint(forward)
        self.centre_axis.setPos(centre_axis.getX(),0.0,centre_axis.getY())

    def update(self):
        """ update the HUD display """
        velocity = self.model.velocity()
        normalized_velocity = velocity * 1.0
        normalized_velocity.normalize()
        
        quat = self.model.quat()
        forward = quat.getForward()
        
        self.staticElementUpdate(forward)
        
        # estimate the screen point which best describes the velocity vector
        velocity_axis = self.getScreenPoint(normalized_velocity)
        self.velocity_indicator.setPos(velocity_axis.getX(),0.0,velocity_axis.getY())

        # for the pitch ladder we need to know where the horizon is and what
        #       is level so we get the forward vector, set the z component to 0
        #       and re-normalise it.
        levelforward = forward * 1.0
        levelforward.setZ(0.0)
        levelforward.normalize()

        heading,pitch,roll = quat.getHpr()
        for angle,line in self.pitchlines.iteritems():
            # although we have defined all the pitch lines, there is certainly
            #       no reason to display them all..
            if angle > pitch - 45 and angle < pitch + 45:
                # adding a vector with the tan of the angle rotates the 
                #       normalised level vector to that angle
                pitchedline = levelforward + Vec3(0.0,0.0,tan(radians(angle)))
                pitchedline.normalize()
                # calculate the appropriate screen position for this vector
                pitched_axis = self.getScreenPoint(pitchedline)
                
                # roll the line so that it is level with the horizon
                line.setR(-roll)
                # and move to the calculated position
                line.setPos(pitched_axis.getX(),0.0,pitched_axis.getY())
                
                # finally we modify the numbers associated with the lines..
                # the following transformations are specified relative to
                # the lines
                
                # as we don't have numbers on the zero line..
                if angle != 0:
                    # line rotation caused the numbers to rotate so we'll 
                    # rotate back
                    self.pitchnumbersL[angle][1].setR(roll)
                    self.pitchnumbersR[angle][1].setR(roll)
                    # and now move them along to either side of the lines
                    self.pitchnumbersL[angle][1].setPos(-0.6,0.0,0)
                    self.pitchnumbersR[angle][1].setPos(0.6,0.0,0)
            else:
                # in all other cases we'll just make sure that the graphic
                # is off the screen
                line.setPos(-2,0.0,-2)

        # some corrections needed for the heading for standard definition
        heading = - round(heading,0)
        if heading < 0.0:
            # no negative angles
            heading += 360.0

        # format for heading will be 000 (includes leading zeros)
        #       abs required to avoid -00 display instead of 000
        head = '%03.0f' %abs(heading)

        #format for climb rate always includes the sign
        climb = '%+7.1f' %velocity.getZ()
        alt = '%6d' %int(self.model.altitude())

        # velocity is converted to km/h (1 m/s = 3.6 km/h)
        vel = '%4d' %int(self.model.speed()*3.6)
        # alpha (angle of attack) includes a unicode greek alpha character
        alpha = u'\u03b1: %5.1f' %round(degrees(self.model.angleOfAttack()),1)
        tgf = 'G: % 5.1f' %round(self.model.gForceTotal(),1)

        self.heading_text.setText(head)
        self.climb_text.setText(climb)
        self.altitude_text.setText(alt)
        self.velocity_text.setText(vel)
        self.total_gforce_text.setText(tgf)
        self.alpha_text.setText(alpha)


    def createOnscreenText(self,pos=(0.0,0.0),align=TextNode.ACenter,
                        scale=None,colour=None,framecolour=(1,1,1,0)):
        """ slight simplification of OnscreenText object creation """
        if colour is None:
            colour = self.colour
        if scale is None:
            scale = self.default_element_scale
        ost = OnscreenText(style=1,fg=colour,pos=pos,align=align,scale=scale,
                           frame=framecolour)
        ost.setFont(self.unicodefont)
        return ost

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
        text_node.setFont(self.unicodefont)
        text_node.setTextColor(colour[0],colour[1],colour[2],colour[3])

        generated_text = text_node.generate()
        text_node_path = render2d.attachNewNode(generated_text)
        text_node_path.setPos(pos[0],0.0,pos[1])
        return text_node,text_node_path

    def createPitchLine(self,points=[0.5,0.25,-0.25,-0.5],
                            tick=0.00,colour=None):
        """ create a line to hint at the pitch of the aircraft on the hud """
        if colour is None:
            colour = self.colour

        pline = LineNodePath(aspect2d,'pitchline',1,Vec4(colour[0],colour[1],
                                                       colour[2],colour[3]))

        plist = []
        for p in points:
            plist.append((p,0.0,0.0))
        plist.insert(0,(points[0],0.0,tick))
        plist.append((points[3],0.0,tick))

        linelist = []
        linelist = [[plist[p],plist[p+1]] for p in range(len(plist)-1)]
        linelist.pop(2)

        pline.drawLines(linelist)
        pline.create()
        return pline

    def createPitchLineOld(self,points=[0.5,0.25,-0.25,-0.5],
                            tick=0.00,colour=None):
        """ create a line to hint at the pitch of the aircraft on the hud """
        if colour is None:
            colour = self.colour

        l = LineNodePath(aspect2d,'pitchline',4,Vec4(colour[0],colour[1],
                                                       colour[2],colour[3]))

        plist = []
        for p in points:
            plist.append((p,0.0,0.0))
        plist.insert(0,(points[0],0.0,tick))
        plist.append((points[3],0.0,tick))

        linelist = []
        linelist = [[plist[p],plist[p+1]] for p in range(len(plist)-1)]
        linelist.pop(2)
        l.drawLines(linelist)
        l.create()

        # These lines are drawn from scratch rather than using a graphic file

        format = GeomVertexFormat.getV3()
        vdata = GeomVertexData("vertices",format,Geom.UHStatic)

        # create vertices to add to use in creating lines
        vertexWriter=GeomVertexWriter(vdata,"vertex")
        # here we define enough positions to create two separated lines
        for p in points:
            vertexWriter.addData3f(p,0.0,0.0)
        # and another two positions for the 'ticks' at the line ends
        vertexWriter.addData3f(points[0],0.0,tick)
        vertexWriter.addData3f(points[3],0.0,tick)

        # create the primitives
        line = GeomLines(Geom.UHStatic)
        line.addVertices(4,0) # the tick part
        line.addVertices(0,1) # part of the horizontal line
        line.closePrimitive()
        line2 = GeomLines(Geom.UHStatic)
        line2.addVertices(2,3) # other part of the horizontal line
        line2.addVertices(3,5) # second tick
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

        cmline = LineNodePath(aspect2d,'centremark',1,Vec4(colour[0],colour[1],
                                                       colour[2],colour[3]))

        plist = []
        plist.append((0.15,0.0,0.0))
        plist.append((0.10,0.0,0.0))
        plist.append((0.05,0.0,-0.025))
        plist.append((0.00,0.0,0.025))
        plist.append((-0.05,0.0,-0.025))
        plist.append((-0.10,0.0,0.0))
        plist.append((-0.15,0.0,0.0))

        linelist = []
        linelist = [[plist[p],plist[p+1]] for p in range(len(plist)-1)]
        cmline.drawLines(linelist)
        cmline.create()
        return cmline

    def createCentreMarkOld(self,colour=None):
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

class MainMenu(object):
    def __init__(self):
        mainmenu = [("Adventure", lambda: base.core.request("World")),
                    ("Quick Game", lambda: self.p("not yet implemented")),
                    ("Credits", lambda: self.p("not yet implemented")),
                    ("Exit", sys.exit)]
        self.font = loader.loadFont("fonts/aranea.ttf")
        self.font.setPixelsPerUnit(100)
        self.parent_node = aspect2d.attachNewNode("main menu")
        self.bg = OnscreenImage(image="backdrops/menubg.jpg",
                                scale=(1.333333,1,1), parent=self.parent_node)
        self.t = OnscreenText("Azure", pos=(-0.6, 0.7), font=self.font,
                              fg=(1,1,1,1), scale=0.3)
        margin = 0.0
        button_options = {
                "text_fg":(1,1,1,1), "text_font":self.font, "text_scale":0.1,
                "relief":None, "rolloverSound":None, "clickSound":None,
                "pressEffect":0, "frameVisibleScale":(0.1,0.1), "sortOrder":2,
                "text_wordwrap":7, "parent":self.parent_node}
        
        self.buttons = []
        lengths = 0
        for caption, function in mainmenu:
            b = DirectButton(text=caption, command=function, **button_options)
            self.buttons.append(b)
            lengths += b.getWidth()
        space = (2 - margin * 2 - lengths) / (len(self.buttons) - 1)
        pos = -1 + margin
        for b in self.buttons:
            pos -= b.node().getFrame()[0]
            b.setPos(pos, 0, -0.7)
            pos += b.node().getFrame()[1] + space

    def p(self, arg):
        """Temporary convenience function."""
        print arg

    def destroy(self):
        self.parent_node.removeNode()
        self.bg.destroy()
        self.t.destroy()
        for b in self.buttons:
            b.destroy()
