"""Here are all the scenarios, missions and gameplays."""

from pandac.PandaModules import AmbientLight, DirectionalLight
from pandac.PandaModules import VBase3, Vec4
from direct.directtools.DirectGrid import DirectGrid
from aircrafts import Aeroplane
from scenery import Scenery, setSky
import gui
import views
from controls import ControlManager


class Scenario(object):
    """Scenarios contain missions."""
    #def __init__(missions)
    #    pass
    def listMissions(self):
        pass


class Mission(object):
    """General Mission class. Inherit from it in the more special missions."""
    def start(self):
        pass
    def stop(self):
        pass


class Sandbox(Scenario):
    """Sandbox is free flying around."""
    def __init__(self):
        pass

class Race(Mission):
    """Race gameplay mode."""
    def __init__(self):
        self.track = None
        self.opponents = ()
        self.current_rank = 0
        self.checkpoints = None



class TestEnvironment(Sandbox):
    """Draw some test grid and stuff."""
    def __init__(self):
        self.grid = DirectGrid(2000, 20, parent=render)
        self.grid.setZ(-0.001)
        setSky("bluesky")

        # lights
        dlight = DirectionalLight("dlight")
        dlnp = render.attachNewNode(dlight)
        dlight.setColor(Vec4(1.0, 0.9, 0.8, 1))
        dlnp.setY(30)
        dlnp.setP(-60)
        render.setLight(dlnp)

        alight = AmbientLight("alight")
        alight.setColor(Vec4(0.6, 0.6, 0.8, 1))
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)

        # load our plane(s)
        self.planes = {}
        base.player = self.planes["player"] = Aeroplane("griffin2")

        # load some others
        pirate1 = Aeroplane("griffin2")
        pirate1.node().setPosHpr(-15, -20, 12, -10, -10, 20)

        pirate2 = Aeroplane("griffin2")
        pirate2.node().setPosHpr(18, -30, 6, 5, -5, -5)

        # set default camera
        #self.default_cam = views.PlaneCamera(base.player.node())
        #self.hud = gui.HUD(base.player.node(), base.camera)
        #self.hud.update()

        cm = ControlManager() 
        cm.request("Fly")
