"""Here are all the scenarios, missions and gameplays."""

from pandac.PandaModules import AmbientLight, DirectionalLight
from pandac.PandaModules import VBase3, Vec4
from pandac.PandaModules import ClockObject
from direct.directtools.DirectGrid import DirectGrid
from pandac.PandaModules import OdeWorld, Vec3

from aircrafts import Aeroplane
from scenery import Scenery, Sky, Water
import gui
import views
import controls


class Scenario(object):
    """Kind of metaclass for all scenario classes.
    A scenario defines a plan for a certain time of gameplay. Think of it like
    chapters in a book."""

    global_clock = ClockObject.getGlobalClock()

    @classmethod
    def list(cls):
        return cls.__subclasses__()

    @classmethod
    def names(cls):
        return [c.__name__ for c in cls.__subclasses__()]

    def __init__(self):
        pass
#    def request(self, scenario_name):
#        base.core.request(scenario_name)

class Mission(object):
    """General Mission class. Inherit from it in the more special missions.
    A mission means you have one or multiple goals and possibly a reward.
    Missions are started in scenarios and ended either by themselves or by the
    scenario."""
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
    """Development Environment."""
    def __init__(self):
        """Everything here happens under a curtain."""
        Scenario.__init__(self)

        self.controls = []

        #self.grid = DirectGrid(2000, 20, parent=render)
        #self.grid.setZ(-0.001)
        water = Water()
        sky = Sky("bluesky")

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

        #big = Scenery("B1G", "big", VBase3(-100, 900, 100),
        #              VBase3(100, 100, 100))

        # initialise physics engine
        #base.enableParticles()

        # load our plane(s)
        base.player = Aeroplane("griffin", "griffin", True)
        base.player.node.setZ(10)
        base.player.physics.setVelocity(Vec3(0,300,0))
        base.player.physics.thrust = 1
        base.player_camera = views.PlaneCamera(base.player)

        # load some others
        #pirate1 = Aeroplane("griffin")
        #pirate1.node.setPos(10, 10, 10)
        #pirate2 = Aeroplane("griffin")
        #pirate2.node.setPosHpr(18, -30, 0, 5, -5, -5)

        # Warning! Leaking! Slows down things at pause+resume
        #base.player.hud = gui.HUD(base.player, base.camera)

        self.indicatorsTL = gui.Indicators(parent=base.a2dTopLeft)
        self.indicatorsTL.add("speed", base.player.physics.speed, vartype=int)
        self.indicatorsTL.add("thrust", base.player.physics.getThrust,
                            vartype=(round, 1))
        self.indicatorsBR = gui.Indicators(parent=base.a2dBottomRight)
        self.indicatorsBR.add("x", base.player.node.getX, vartype=(int))
        self.indicatorsBR.add("y", base.player.node.getY, vartype=(int))
        self.indicatorsBR.add("z", base.player.node.getZ, vartype=(int))

        self.controls.append(controls.Debug())
        self.controls.append(controls.PlaneFlight())
        self.controls.append(controls.Pause())

    def start(self):
        """Here the curtain is taken off and the interaction begins."""
        #base.player.hud.update()
        # TODO(Nemesis#13): reset delta time of GlobalClock
        #Scenario.global_clock.setDt(0.0000001)  # doesn't work
        base.player.node.setY(0)  # workaround
        for control in self.controls:
            control.activate()


class Tutorial(Scenario):
    """Introduce the player to the controls."""
    def __init__(self):
        Scenario.__init__(self)
