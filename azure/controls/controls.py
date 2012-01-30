"""Module for everything about controls."""

from ConfigParser import SafeConfigParser, NoSectionError

from panda3d.core import ExecutionEnvironment as EE
from panda3d.core import Filename
from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.directnotify.DirectNotify import DirectNotify

import gui
from views import PlaneCamera
from errors import AzureError


notify = DirectNotify().newCategory("azure-control")





#-----------------------------------------------------------------------------


class Pause(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"toggle": "p"}
        self.functionmap = {"toggle": self.togglePause}
        self.paused_states = []
        self.paused = False

    def pauseOn(self):
        for state in list(ControlState.active_states):
            if state.paused:
                state.deactivate()
                self.paused_states.append(state)
        taskMgr.setupTaskChain("world", frameBudget=0)
        from gui import PauseMenu
        self.menu = PauseMenu()

    def pauseOff(self):
        for state in self.paused_states:
            state.activate()
        self.paused_states = []
        taskMgr.setupTaskChain("world", frameBudget=-1)
        self.menu.destroy()

    def togglePause(self):
        self.pauseOff() if self.paused_states else self.pauseOn()

    def status(self):
        """Returns True if paused."""
        return self.paused_states != []


class PlaneFlight(ControlState):
    """A control state for flying a plane."""
    def __init__(self, plane, view):
        ControlState.__init__(self)
        self.keymap = {"move.roll-left":        "a",
                       "move.roll-right":       "d",
                       "move.pitch-up":         "s",
                       "move.pitch-down":       "w",
                       "move.heading-left":     "q",
                       "move.heading-right":    "e",
                       "thrust.add":            "page_up",
                       "thrust.subtract":       "page_down",
                       "camera.next":           "c",
                       "camera.prev":           "shift-c",
                       "camera.third-person":   "1",
                       "camera.first-person":   "2",
                       "camera.cockpit":        "3",
                       "camera.detached":       "4",
                       "camera.sideview":       "5"
                      }
        self.functionmap = {"camera.next":
                            lambda: self.plane_camera.setView("Next"),
                            "camera.prev":
                            lambda: self.plane_camera.setView("Prev"),
                            "camera.third-person":
                            lambda: self.plane_camera.setView("ThirdPerson"),
                            "camera.first-person":
                            lambda: self.plane_camera.setView("FirstPerson"),
                            "camera.cockpit":
                            lambda: self.plane_camera.setView("Cockpit"),
                            "camera.detached":
                            lambda: self.plane_camera.setView("Detached"),
                            "camera.sideview":
                            lambda: self.plane_camera.setView("Sideview")
                           }

        #self.tasks = (self.flightControl, self.updateHUD)
        self.tasks = (self.flightControl,)
        self.plane = plane
        self.plane_camera = view

    def flightControl(self, task):
        """Move the plane acording to pressed keys."""
        for action in self.requested_actions:
            a = action.split(".")[0]
            if a == "move":
                self.plane.physics.move(action.split(".")[1])
            elif a == "thrust":
                self.plane.physics.chThrust(action.split(".")[1])
        return Task.cont

    # Function leaky! Slows down things at pause+resume
    def updateHUD(self, task):
        if self.plane.hud:
            self.plane.hud.update()
        return Task.cont

    #def switchView(self, task):
    #    actions_done = []
    #    for action in self.requested_actions:
    #        if action.splt(".")[0] == "camera":
    #            request = action.split(".")[1]
    #            # Translate option to class name
    #            view = "".join(x.capitalize() for x in request.split('-'))
    #            self.plane_camera.setView(view)
    #            # Key could be pressed over multiple frames, but we want this
    #            # to be activated only once.
    #            actions_done.add(action)
    #    self.requested_actions -= actions_done
    #    return Task.cont


class Debug(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"print_tasks": "f10",
                       "print_scene": "f11",
                       "screenshot": ["f12", "print_screen"],
         #              "toggle_hud": "f9"
                      }
        self.functionmap = {"screenshot": base.screenshot}
        self.tasks = ([self.debugTask, "debugging task"],)
        self.paused = False

    def debugTask(self, task):
        if "print_scene" in self.requested_actions:
            print
            print "render scene graph:"
            print render.ls()
            print "-" * 40
            print "render2d scene graph:"
            print render2d.ls()
            print
        if "print_tasks" in self.requested_actions:
            print base.taskMgr

        self.requested_actions.clear()
        return Task.cont

class FreeCameraFlight(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {}


class IngameMenu(ControlState):
    """A control state for in-game menus (e.g. pause menu)."""
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"back":      "escape",
                       "activate":  ["enter", "space"],
                       "go_up":     ["arrow_up", "wheel_up", "w"],
                       "go_down":   ["arrow_down", "wheel_down", "s"]
                      }
        #self.tasks = (self.menuControl,)

    #def menuControl(self):
    #    pass


class Sequence(ControlState):
    """Control state for ingame sequences."""
    def __init__(self):
        ControlState.__init__(self)
        keymap = {"ask_skip": "escape"}
        self.tasks = (self.skipSequence,)

    def skipSequence(self):
        pass
