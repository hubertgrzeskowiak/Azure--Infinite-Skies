import sys

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task


class MainMenu(object):
    """Draw a nice menu with some choices."""
    def __init__(self):
        mainmenu = [("Adventure", lambda: base.core.demand("Loading",
            "Developmentenvironment")),
                    ("Quick Game", lambda: self.p("not yet implemented")),
                    ("Credits", lambda: self.p("not yet implemented")),
                    ("Exit", sys.exit)]
        self.font = loader.loadFont("fonts/aranea.ttf")
        self.font.setPixelsPerUnit(100)
        self.parent_node = aspect2d.attachNewNode("main menu")
        self.bg = OnscreenImage(image="backdrops/menubg.jpg",
                                scale=(4.0/3,1,1), parent=self.parent_node)
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
