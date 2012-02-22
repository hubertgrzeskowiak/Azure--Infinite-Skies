"""This is a proof of concept main menu."""

import os

from panda3d.rocket import *
from panda3d.core import Point3
from direct.directbase import DirectStart
from direct.interval.IntervalGlobal import Sequence, Parallel

LoadFontFace("aranea.ttf")
LoadFontFace("LinLibertine_R.ttf")
LoadFontFace("FreeSerif.ttf")

r = RocketRegion.make('pandaRocket', base.win)
r.setActive(1)
r.initDebugger()
r.setDebuggerVisible(1)
context = r.getContext()

#context.LoadDocument('data/background.rml').Show()

doc = context.LoadDocument('main_menu.rml')
doc.Show()

ih = RocketInputHandler()
base.mouseWatcher.attachNewNode(ih)
r.setInputHandler(ih)




base.disableMouse()
base.setBackgroundColor(0.4, 0.6, 0.76)
g = loader.loadModel("../resources/planes/griffin/griffin")
g.reparentTo(render)
i1 = g.posInterval(1, Point3(.0,.0,0.3), startPos=Point3(.0,.0,-0.3))
i2 = g.posInterval(1, Point3(.0,.0,-0.3), startPos=Point3(.0,.0,0.3))
i3 = g.hprInterval(1.4, Point3(.0,.0,-1), startHpr=Point3(.0,.0,1))
i4 = g.hprInterval(1.4, Point3(.0,.0,1), startHpr=Point3(.0,.0,-1))
Sequence(i1, i2, name="foo").loop()
Sequence(i3, i4, name="bar").loop()
base.cam.setPos(-17, -23, 5)
base.cam.lookAt(g.getPos()+(0,15,0))
base.cam.setR(5)


run()
