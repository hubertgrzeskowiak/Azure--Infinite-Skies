"""Module containing graphical user interface objects"""

from direct.gui.DirectGui import OnscreenText
from pandac.PandaModules import TextNode
from math import degrees

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
    def __init__(self,model):
        self.model = model
        self.head = OnscreenText(text="head: ",style=1,fg=(1,1,1,1),
                                     pos=(0.0, 0.95),align=TextNode.ACenter,
                                     scale=0.05)
        self.alt = OnscreenText(text="alt: ",style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.vel = OnscreenText(text="vel: ",style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.85),align=TextNode.ALeft,
                                     scale=0.05)
    def update(self):
        heading = - self.model.dummy_node.getH()
        if heading < 0.0:
            heading += 360.0
        head = '%.1f' %abs(round(heading,1))
        alt = 'alt: %d' %int(self.model.dummy_node.getZ())
        vel = 'vel: %d' %int(self.model.velocity_v.length())
        
        self.head.destroy()
        self.alt.destroy()
        self.vel.destroy()
        self.head = OnscreenText(text=head,style=1,fg=(1,1,1,1),
                                     pos=(0.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.alt = OnscreenText(text=alt,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.95),align=TextNode.ALeft,
                                     scale=0.05)
        self.vel = OnscreenText(text=vel,style=1,fg=(1,1,1,1),
                                     pos=(1.0, 0.85),align=TextNode.ALeft,
                                     scale=0.05)
