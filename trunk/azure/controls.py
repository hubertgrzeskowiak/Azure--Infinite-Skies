"""Module for everything about controls."""

import sys
from direct.showbase.DirectObject import DirectObject
from direct.fsm.FSM import FSM
from direct.task import Task
import views

class KeyHandler(DirectObject):
    """Gets key events and does stuff."""

    def __init__(self):
        self.key_states = {}

    def chKeyState(self, key, value):
        #print("key %s changed to %d" % (key, value))
        self.key_states[key] = value

    def mountControlmap(self, controlmap):
        """Mount a controlmap dict."""
        self.controlmap = controlmap

        # non-continous keys (direct action, no state saving)
        self.accept("escape", sys.exit)
        
        # continuous keys
        for key in self.controlmap:
            # at start no key is active
            self.key_states[key] = 0
            # go through keys and 'accept' them
            self.accept(key, self.chKeyState, [key, 1])
            self.accept(key+"-up", self.chKeyState, [key, 0])

        
class Controlmaps(object):
    """Some control maps."""

    flight = {
        "a": ("move", "roll-left"),
        "d": ("move", "roll-right"),
        "s": ("move", "pitch-up"),
        "w": ("move", "pitch-down"),
        "q": ("move", "heap-right"),
        "e": ("move", "heap-left"),
        "page_up": ("thrust", "add"),
        "page_down": ("thrust", "subtract"),
        "p": ("cam-view", views.FIRST_PERSON),
        "o": ("cam-view", views.COCKPIT),
        "i": ("cam-view", views.THIRD_PERSON),
        "u": ("cam-view", views.DETACHED)
        }


class ControlManager(FSM):
    """A finite state machine which determines current controls and player
    status."""
    def __init__(self):
        FSM.__init__(self, "playerFSM")
        self.k = KeyHandler()

    def enterFly(self):
        self.k.mountControlmap(Controlmaps.flight)
        self.fly_task = taskMgr.add(self.flyTask, "flyTask")
    def exitFly(self):
        pass
        #TODO: implement this..


    def flyTask(self, task):
        """Move the plane acording to pressed keys."""
        for key, state in self.k.key_states.items():
            if state == 1:
                # key_info is a tuple of an action and a value (both strings)
                key_info = Controlmaps.flight[key]
                if key_info[0] == "move":
                    base.player.move(key_info[1])
                elif key_info[0] == "thrust":
                    base.player.chThrust(key_info[1])
        #base.player.reverseRoll()
        #base.player.reversePitch()
        base.player.velocityForces()
        return Task.cont
