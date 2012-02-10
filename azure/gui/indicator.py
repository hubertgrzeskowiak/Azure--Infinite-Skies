from collections import OrderedDict

from pandac.PandaModules import TextNode
from direct.gui.DirectGui import *
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from azure.utils import sign


class Indicator(object):
    """One single onscreen indicator that shows a label and the return value of
    an assigned function. To be used in debugging."""
    indent = 0.5  # distance label<->value
    def __init__(self, name, func, color=(0,0,0,1), bg_color=None,
                 parent=None):
        """Arguments:
        name -- the visible label. should be unique
        func -- a function that gives a value to display. use lambda for extra
                arguments.
        color -- indvidual color for that indicator
        parent -- which corner to move to
        """
        self.opts = {"fg":color, "bg":bg_color,
                     "parent":parent or base.a2dBottomRight}
        self.name = name
        self.func = func
        self.label = OnscreenText(text=name+":", align=TextNode.ALeft,
                                  mayChange=True, scale=0.04, **self.opts)
        self.value = OnscreenText(text="", align=TextNode.ARight,
                                  mayChange=True, scale=0.04, **self.opts)
        self.value.setX(self.indent)

    def destroy(self):
        self.label.destroy()
        self.value.destroy()
