"""Here are all the scenarios, missions and gameplays."""

from pandac.PandaModules import AmbientLight, DirectionalLight
from pandac.PandaModules import VBase3, Vec4
from direct.directtools.DirectGrid import DirectGrid
from pandac.PandaModules import OdeWorld

from aircrafts import Aeroplane
from scenery import Scenery, Sky, Water
import gui
import views
import controls


class Scenario(object):
    """Kind of metaclass for all scenario classes."""
    @classmethod
    def list(cls):
        return cls.__subclasses__()

    @classmethod
    def names(cls):
        return [c.__name__ for c in cls.__subclasses__()]

#    def request(self, scenario_name):
#        base.core.request(scenario_name)

class Mission(object):
    """General Mission class. Inherit from it in the more special missions."""
    @classmethod
    def list(cls):
        return cls.__subclasses__()

    @classmethod
    def names(cls):
        return [c.__name__ for c in cls.__subclasses__()]

    def __init__(self):
        self.active = False

    def start(self):
        pass

    def stop(self):
        pass

#------------------------------------------------------------------------------


class Race(Mission):
    def __init__(self):
        self.track = None
        self.opponents = ()
        self.current_rank = 0
        self.checkpoints = None


class TestEnvironment(Scenario):
    """Draw some test grid and stuff."""
    def __init__(self):
        # initialise ODE
        world = OdeWorld()
        #world.setGravity(0.0, 0.0, -9.81)
        world.setGravity(0.0, 0.0, 0.0)
        
        #self.grid = DirectGrid(2000, 20, parent=render)
        #self.grid.setZ(-0.001)
        #setSky("bluesky")
        sky = Sky("bluesky")
        water = Water()

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
        base.player = Aeroplane("griffin", world=world)
        base.player_camera = views.PlaneCamera(base.player)
        self.control = controls.PlaneFlight()

        # load some others
        #pirate1 = Aeroplane("griffin")
        #pirate1.node.setPosHpr(-15, -20, 12, -10, -10, 20)

        #pirate2 = Aeroplane("griffin")
        #pirate2.node.setPosHpr(18, -30, 6, 5, -5, -5)

        # set default camera
        base.player.hud = gui.HUD(base.player, base.camera)
        base.player.hud.update()
        self.control.activate()

    def start(self):
        pass

#class MainMenu(Menu):
#    def __init__(self):
#        gui.MainMenu()
