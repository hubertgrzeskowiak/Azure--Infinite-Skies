"""Module for everything about controls."""

import sys

from direct.showbase.DirectObject import DirectObject

import views

class keyHandler(DirectObject):
    """Gets key events and does stuff."""

    def __init__(self, ctlMap):
        """Takes a controls map as argument and writes keys' states into a
        callable dict."""
        
        self.ctlMap = ctlMap
        
        # non-continous keys (direct action, no state saving)
        self.accept("escape", sys.exit)
        
        # continuous keys
        self.keyStates = {}
        for key in self.ctlMap.controls:
            # at start no key is active
            self.keyStates[key] = 0
            # go through keys and 'accept' them
            self.accept(key, self.chKeyState, [key, 1])
            self.accept(key+"-up", self.chKeyState, [key, 0])

    def chKeyState(self, key, value):
        #print("key %s changed to %d" % (key, value))
        self.keyStates[key] = value
        
class controlMap():
    """Default controls map."""

    def __init__(self):
        self.controls = {
            "a": {"type":"move", "desc": "roll-left"},
            "d": {"type":"move", "desc": "roll-right"},
            "s": {"type":"move", "desc": "pitch-up"},
            "w": {"type":"move", "desc": "pitch-down"},
            "q": {"type":"move", "desc": "heap-right"},
            "e": {"type":"move", "desc": "heap-left"},
            "space": {"type":"move", "desc": "move-forward"},
            "=": {"type":"move", "desc": "increase-thrust"},
            "+": {"type":"move", "desc": "increase-thrust"},
            "-": {"type":"move", "desc": "decrease-thrust"},
            "z": {"type":"cam-move", "desc": "move-left"},
            "c": {"type":"cam-move", "desc": "move-right"},
            "x": {"type":"cam-move", "desc": "move-origin"},
            "p": {"type":"cam-view", "desc": views.FIRST_PERSON},
            "o": {"type":"cam-view", "desc": views.COCKPIT},
            "i": {"type":"cam-view", "desc": views.THIRD_PERSON},
            "u": {"type":"cam-view", "desc": views.DETACHED}
            }
