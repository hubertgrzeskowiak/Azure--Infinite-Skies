"""Module for everything about controls."""

import sys
import os
from ConfigParser import SafeConfigParser, NoSectionError

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.directnotify.DirectNotify import DirectNotify

import gui
from views import PlaneCamera
from errors import AzureError


notify = DirectNotify().newCategory("azure-control")


class ControlState(DirectObject):
    """Specific control state classes should inherit from this.
    Control States are a kind of FSM, but instead of multiple states per FSM
    where one or none is active at a time you have single states you turn on
    and off. By instancing states in states you can have collections of certain
    behaviors inside simple classes. 
    """
    conf_parser = SafeConfigParser()
    conf_parser.read(os.path.abspath(os.path.join(sys.path[0],
                                     "etc/keybindings.ini")))
    active_states = []


    @classmethod
    def reloadKeybindings(cls, filenames="etc/keybindings.ini"):
        """Read the keybindings file again. Existing instances won't update
        until you call loadKeybindings() on them."""
        cls.conf_parser.read(filenames)

    def __init__(self):
        self.name = self.__class__.__name__
        # format for keymap: keymap["action"] = "key1, key2"
        #                 or keymap["action"] = "key"
        self.keymap = {}
        # format for functionmap: functionmap["action"] = function
        self.functionmap = {}
        self.requested_actions = set()
        self.tasks = ()
        self.no_pause = False
        self.active = False

    def __repr__(self):
        return self.name

    def loadKeybindings(self):
        """Overrides the hardcoded keymap with those found in the
        keybindings file. Only defined actions are overwritten - no extra
        actions are added from the keybindings file."""
        try:
            keys_from_file = ControlState.conf_parser.items(self.name)
            for a in self.keymap:
                for action, key in keys_from_file:
                    if a == action:
                        for k in map(str.strip, key.split(',')):
                            self.keymap[a] = k
        except NoSectionError:
            notify.warning("Keybindings for section %s not found. Using built-in bindings" % self.name)

    def activate(self):
        if self.active is True:
            "activating an active state: %s" % self.name
            return False
        notify.info("Activating %s" % self.name)

        def assignKey(key, action):
            self.accept(key, self.requested_actions.add, [action])
            self.accept(key+"-up", self.requested_actions.discard, [action])
            if action in self.functionmap:
                self.accept(key, self.functionmap[action])

        for action, key in self.keymap.items():
            if isinstance(key, basestring):
                assignKey(key, action)
            elif isinstance(key, list):
                for k in key:
                    assignKey(k, action)

        self.loadKeybindings()

        for task in self.tasks:
            self.addTask(task, task.__name__)
        self.active = True
        ControlState.active_states.append(self)

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
        ControlState.active_states.remove(self)

#-----------------------------------------------------------------------------


class Pause(ControlState):
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"toggle": "p"}
        self.functionmap = {"toggle": self.togglePause}
        self.paused_states = []
        self.no_pause = True

    def pauseOn(self):
        for state in list(ControlState.active_states):
            if not state.no_pause:
                state.deactivate()
                self.paused_states.append(state)

    def pauseOff(self):
        for state in self.paused_states:
            state.activate()
        self.paused_states = []

    def togglePause(self):
        if self.paused_states:
            self.pauseOff()
        else:
            self.pauseOn()

    def status(self):
        """Returns True if paused."""
        return self.paused_states != []


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
                       "camera.next":           "c",
                       "camera.prev":           "shift-c",
                       "camera.third-person":   "1",
                       "camera.first-person":   "2",
                       "camera.cockpit":        "3",
                       "camera.detached":       "4",
                       "camera.sideview":       "5"
                      }
        self.functionmap = {"camera.next":
                            lambda: base.player_camera.setView("Next"),
                            "camera.prev":
                            lambda: base.player_camera.setView("Prev"),
                            "camera.third-person":
                            lambda: base.player_camera.setView("ThirdPerson"),
                            "camera.first-person":
                            lambda: base.player_camera.setView("FirstPerson"),
                            "camera.cockpit":
                            lambda: base.player_camera.setView("Cockpit"),
                            "camera.detached":
                            lambda: base.player_camera.setView("Detached"),
                            "camera.sideview":
                            lambda: base.player_camera.setView("Sideview")
                           }

        self.tasks = (self.fly, self.updateHUD)

    def fly(self, task):
        """Move the plane acording to pressed keys."""
        for action in self.requested_actions:
            a = action.split(".")[0]
            if a == "move":
                base.player.move(action.split(".")[1])
            elif a == "thrust":
                base.player.chThrust(action.split(".")[1])
        return Task.cont

    def updateHUD(self, task):
        if base.player.hud:
            base.player.hud.update()
        return Task.cont

    #def switchView(self, task):
    #    actions_done = []
    #    for action in self.requested_actions:
    #        if action.splt(".")[0] == "camera":
    #            request = action.split(".")[1]
    #            # Translate option to class name
    #            view = "".join(x.capitalize() for x in request.split('-'))
    #            base.player_camera.setView(view)
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
        self.tasks = (self.debugTask,)

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
        #if "toggle_hud" in self.requested_actions:
        #    if base.player.hud:
        #        base.player.hud.destroy()
        #        base.player.hud = None
        #    else:
        #        base.player.hud = gui.HUD(base.player, base.camera)

        self.requested_actions.clear()
        return Task.cont


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
