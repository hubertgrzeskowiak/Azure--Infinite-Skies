"""Module for everything about controls."""

import sys
import os
from ConfigParser import SafeConfigParser

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.directnotify.DirectNotify import DirectNotify

from views import PlaneCamera
from errors import AzureError


notify = DirectNotify().newCategory("azure-control")

class ControlState(DirectObject):
    """Specific control state classes should inherit from this.
    Every derived class is expected to have a list of keybindings and tasks."""
    conf_parser = SafeConfigParser()
    conf_parser.read(os.path.abspath(os.path.join(sys.path[0], "etc/keybindings.ini")))
    active_states = []

    @classmethod
    def reloadKeybindings(cls, filenames="etc/keybindings.ini"):
        """Read the keybindings file again. Existing instances won't update
        until you call loadKeybindings() on them."""
        cls.conf_parser.read(filenames)

    def __init__(self):
        self.name = self.__class__.__name__
        self.keymap = {}
        self.requested_actions = set()
        self.tasks = ()
        self.active = False

    def loadKeybindings(self):
        """Overrides the builtin keymap with those found in the
        keybindings file."""
        try:
            keys_from_file = ControlState.conf_parser.items(self.name)
            for a in self.keymap:
                for action, key in keys_from_file:
                    if a == action:
                        self.keymap[a] = key
        except "NoSectionError":
            notify.warning("Keybindings for section $s not found. "
                           "Using built-in bindings" % self.name)

    def activate(self):
        if self.active is True:
            return False
        notify.info("Activating %s" % self.name)
        if self.keymap != ():
            self.loadKeybindings()
            for action, key in self.keymap.items():
                if isinstance(key, basestring):
                    self.accept(key, self.requested_actions.add, [action])
                    self.accept(key+"-up", self.requested_actions.discard, [action])
                else:
                    for k in key:
                        self.accept(k, self.requested_actions.add, [action])
                        self.accept(k+"-up", self.requested_actions.discard, [action])
        for task in self.tasks:
            self.addTask(task, task.__name__)
        self.active = True
        ControlState.active_states.add(self)

    def deactivate(self):
        if self.active is False:
            return False
        notify.info("Deactivating %s" % self.name)
        self.ignoreAll()
        self.requested_actions.clear()
        #for task in self.tasks:
        #    self.removeTask(task)
        self.removeAllTasks()
        self.active = False
        ControlState.active_states.discard(self)

#-----------------------------------------------------------------------------

class PlaneFlight(ControlState):
    """A control state for flying a plane."""
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"move.roll-left":        "a",
                       "move.roll-right":       "d",
                       "move.pitch-up":         "s",
                       "move.pitch-down":       "w",
                       "move.heading-left":     "q",
                       "move.heading-right":    "e",
                       "thrust.add":            "page_up",
                       "thrust.subtract":       "page_down",
                       "camera.Next":           "c",
                       "camera.Prev":           "shift-c",
                       "camera.ThirdPerson":    "1",
                       "camera.FirstPerson":    "2",
                       "camera.Cockpit":        "3",
                       "camera.Detached":       "4",
                       "camera.Sideview":       "5"
                      }
        self.tasks = (self.flyTask,)

    def flyTask(self, task):
        """Move the plane acording to pressed keys."""
        actions_done = set()

        for action in self.requested_actions:
            a = action.split(".")[0]
            if a == "move":
                base.player.move(action.split(".")[1])
            elif a == "thrust":
                base.player.chThrust(action.split(".")[1])
            elif a == "camera":
                base.player_camera.setView(action.split(".")[1])
                actions_done.add(action)
                # One-timer. Prevent this from being caught
                self.requested_actions -= actions_done

        if base.player.hud:
            base.player.hud.update()
        return Task.cont


class Pause(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"resume": "escape",
                       "resume": "p"}


class Debug(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"printScene": "f12",
                       "screenshot": "f11"}

        self.tasks = (self.debugTask,)

    def debugTask(self, task):
        if "printScene" in self.requested_actions:
            print "-" * 40
            print "render scene graph:"
            print render.ls()
            print "-" * 40
            print "render2d scene graph:"
            print render2d.ls()
            print "-" * 40

        if "screenshot" in self.requested_actions:
            print "%s saved" % base.screenshot()
        self.requested_actions.clear()
        return Task.cont


class GameMenu(ControlState):
    """A control state for in-game menus (e.g. pause menu)."""
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"back":      "escape",
                       "activate":  "enter",
                       "go_up":     "arrow_up",
                       "go_down":   "arrow_down"
                      }
        #self.tasks = (self.menuControl,)

    #def menuControl(self):
    #    pass


class Sequence(ControlState):
    """Control state for ingame sequences."""
    def __init__(self):
        ControlState.__init__(self)
        keymap = {"skip": "escape"}
        self.tasks = (self.skipSequence,)

    def skipSequence(self):
        pass
