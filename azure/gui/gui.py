# -*- coding: utf-8 -*-
"""Module containing graphical user interface objects"""

import sys
from math import degrees, radians, pi, tan, sin, cos

from pandac.PandaModules import GeomVertexFormat,GeomVertexData
from pandac.PandaModules import Geom,GeomNode,GeomVertexWriter,GeomLines
from pandac.PandaModules import TransparencyAttrib
from pandac.PandaModules import TextNode
from pandac.PandaModules import Point3, Point2, Vec3, Vec4
from direct.showbase.DirectObject import DirectObject
from direct.directtools.DirectGeometry import LineNodePath
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.task import Task

#from views import PlaneCamera
#from core import Core

class _Indicator(object):
    """One single onscreen indicator. Used by Indicators class."""
    indent = 0.3  # distance label<->value
    def __init__(self, name, func, func_args=[], vartype=None, color=(0,0,0,1),
                 parent=None):
        """Arguments:
        name -- the visible label. should be unique
        func -- a function that gives a value to display
        func_args -- arguments for the function above (list or dict)
        vartype -- a type converting function like float, int or the like
                if it's a tuple, the first element will be considered the
                function func and others as additional parameters.
                Examples: vartype=int  or  type=(round, 1)
        color -- indvidual color for that indicator
        parent -- which corner to move to
        """
        self.opts = {"fg":color, "parent":parent or base.a2dBottomRight}
        self.name = name
        self.func = func
        self.func_args = func_args
        self.vartype = vartype
        self.label = OnscreenText(text=name+":", align=TextNode.ALeft,
                                  mayChange=True, scale=0.04, **self.opts)
        self.value = OnscreenText(text="", align=TextNode.ARight,
                                  mayChange=True, scale=0.04, **self.opts)
        self.value.setX(self.indent)

    def destroy(self):
        self.label.destroy()
        self.value.destroy()


class Indicators(DirectObject):
    """Draw some debugging info on the screen like speed, thrust etc.."""
    def __init__(self, parent=None, color=(0,0,0,1)):
        """parent can be one of: base.a2dTopCenter, base.a2dBottomCenter,
        base.a2dLeftCenter, base.a2dRightCenter, base.a2dTopLeft,
        base.a2dTopRight, base.a2dBottomLeft, base.a2dBottomRight
        """
        self.indicators = {}  # form: {name: _Indicator}
        self.parent = parent or base.a2dBottomRight
        self.lspacing = 0.04  # line spacing
        self.margin = 0.4  #  margin from screen border
        self.color = color
        self.task = self.addTask(self.updateIndicators,
                                 "Update onscreen debugging infos",
                                 taskChain="world", sort=80)

    def add(self, name, func, func_args=[], vartype=None, color=None):
        """Add a new indicator. Same parameters as _indicator.__init__ ."""
        if self.indicators.has_key(name):
            return False
        self.indicators[name] = _Indicator(name, func, func_args, vartype,
                                           color or self.color, self.parent)
        self.reposition()

    def remove(self, name):
        """Remove an indicator."""
        if self.indicators.has_key(name):
            self.indicators[name].destroy()
            del self.indicators[name]
            self.reposition()
        else:
            return False

    def reposition(self):
        """After removing items or changing the positioning vars, this puts
        everthing into its place.
        """
        if not self.indicators:
            return False

        i = x = y = 0
        parx = self.parent.getX()
        pary = self.parent.getZ()
        if parx != 0:
            x = self.margin * -parx / abs(parx)
            if parx < 0:
                x -= _Indicator.indent
        if pary != 0:
            y = self.margin / 3 * -pary / abs(pary)
        for indicator in self.indicators.values():
            indicator.label.setPos(x, y+self.lspacing*i)
            indicator.value.setPos(x + _Indicator.indent, y+self.lspacing*i)
            i += 1 if pary >= 0 else -1

    def updateIndicators(self, task):
        for name, indicator in self.indicators.items():
            func = indicator.func.__call__
            args = indicator.func_args
            vartype = indicator.vartype

            if not args:
                text = func()
            elif isinstance(args, []):
                text = func(*args)
            elif isinstance(args, {}):
                text = func(**args)

            if vartype:
                if isinstance(vartype, tuple):
                    text = vartype[0].__call__(text, *vartype[1:])
                else:
                    text = vartype.__call__(text)

            indicator.value.setText(str(text))
        return Task.cont

    def destroy(self):
        """Remove all indicators and stop the updating task."""
        self.removeTask(self.task)
        for name, ind in self.indicators.items():
            ind.destroy()
        self.indicators = {}


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

class PauseMenu(object):
    def __init__(self):

        self.dialog = OkDialog(fadeScreen=0.5, text="Game Paused")
        self.dialog.show()

    def destroy(self):
        self.dialog.destroy()
