"""Here are all the scenarios, missions and gameplays."""

from pandac.PandaModules import AmbientLight, DirectionalLight
from pandac.PandaModules import VBase3, Vec4
from direct.directtools.DirectGrid import DirectGrid
from aircrafts import Aeroplane
from scenery import Scenery, setSky
import gui
import views
import controls

from pandac.PandaModules import OdeWorld

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
        # initialise ODE
        world = OdeWorld()
        #world.setGravity(0.0, 0.0, -9.81)
        world.setGravity(0.0, 0.0, 0.0)
        
        self.grid = DirectGrid(2000, 20, parent=render)
        self.grid.setZ(-0.001)
        setSky("bluesky")

        # lights
        sunlight = DirectionalLight("sun")
        sunlight.setColor(Vec4(1.0, 0.9, 0.8, 1))
        sunnp = render.attachNewNode(sunlight)
        sunnp.setP(-60)
        render.setLight(sunnp)

        alight = AmbientLight("alight")
        alight.setColor(Vec4(0.6, 0.6, 0.8, 1))
        alnp = render.attachNewNode(alight)
        render.setLight(alnp)

        #render.setShaderAuto(True)

        ## initialise physics engine
        #base.enableParticles()

        # load our plane(s)
        base.player = Aeroplane("griffin2", world=world)
        base.player_camera = views.PlaneCamera(base.player)
        self.control = controls.PlaneFlight()

        # load some others
        #pirate1 = Aeroplane("griffin2")
        #pirate1.node().setPosHpr(-15, -20, 12, -10, -10, 20)

        #pirate2 = Aeroplane("griffin2")
        #pirate2.node().setPosHpr(18, -30, 6, 5, -5, -5)

        # set default camera
        base.player.hud = gui.HUD(base.player, base.camera)
        base.player.hud.update()
        self.control.activate()
