from collections import OrderedDict

from pandac.PandaModules import TextNode
from direct.gui.DirectGui import *
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from azure.gui import Indicator


class OSDebug(DirectObject):
    """Draw some debugging info on the screen. This mainly
    draws a few lines of labels and corresponding functions' return values.
    """
    def __init__(self, parent=None, color=(0,0,0,1), bg_color=None):
        """parent can be any node. Mostly you'll use one of:
        base.a2dTopCenter, base.a2dBottomCenter,
        base.a2dLeftCenter, base.a2dRightCenter, base.a2dTopLeft,
        base.a2dTopRight, base.a2dBottomLeft, base.a2dBottomRight
        """
        self.indicators = OrderedDict()  # form: {name: Indicator}
        self.parent = parent or base.a2dBottomRight
        self.lspacing = 0.04  # line spacing
        self.margin = 0.5  #  margin from screen border
        self.color = color
        self.bg_color = bg_color
        self.task = self.addTask(self.updateIndicators,
                                 "Update onscreen debugging infos",
                                 taskChain="world", sort=80)

    def add(self, name, func, color=None, bg_color=None):
        """Add a new indicator. Same parameters as _indicator.__init__ ."""
        if self.indicators.has_key(name):
            print "Warning: Indicator {0} already used. Replacing.".format(name)
        self.indicators[name] = Indicator(name, func, color or self.color,
                                          bg_color or self.bg_color, self.parent)
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
        """After adding, removing items or changing the positioning vars, this
        puts everthing into its place.
        """
        if not self.indicators:
            return False

        i = x = y = 0
        parx = self.parent.getX()
        pary = self.parent.getZ()
        if parx != 0:
            x = self.margin * -parx / abs(parx)
            if parx < 0:
                x -= Indicator.indent
        if pary != 0:
            y = self.margin / 3 * -pary / abs(pary)
        for indicator in self.indicators.values():
            indicator.label.setPos(x, y+self.lspacing*i)
            indicator.value.setPos(x + Indicator.indent, y+self.lspacing*i)
            i += 1 if pary >= 0 else -1

    def updateIndicators(self, task):
        for name, indicator in self.indicators.items():
            #print "updating "+name+" with label: "+str(indicator.label.getText())+"and"+\
            #      "func: "+str(indicator.func)
            val = str(indicator.func())
            indicator.value.setText(val)
        return Task.cont

    def destroy(self):
        """Remove all indicators and stop the updating task."""
        self.removeTask(self.task)
        for name, ind in self.indicators.items():
            ind.destroy()
        self.indicators = {}

# TEST
if __name__ == "__main__":
    import random
    import time
    import direct.directbase.DirectStart
    smiley = loader.loadModel("smiley")
    smiley.reparentTo(render)
    smiley.setY(30)

    o = OSDebug(base.a2dTopLeft)
    o.add("x", lambda: round(camera.getX(), 2))
    o.add("y", lambda: round(camera.getY(), 2))
    o.add("z", lambda: round(camera.getZ(), 2))
    o = OSDebug(base.a2dBottomLeft)
    o.add("x", lambda: round(camera.getX(), 2))
    o.add("y", lambda: round(camera.getY(), 2))
    o.add("z", lambda: round(camera.getZ(), 2))
    o = OSDebug(base.a2dTopRight)
    o.add("h", lambda: round(camera.getH(), 2))
    o.add("p", lambda: round(camera.getP(), 2))
    o.add("r", lambda: round(camera.getR(), 2))
    o = OSDebug(base.a2dBottomRight)
    o.add("h", lambda: round(camera.getH(), 2))
    o.add("p", lambda: round(camera.getP(), 2))
    o.add("r", lambda: round(camera.getR(), 2))
    run()
