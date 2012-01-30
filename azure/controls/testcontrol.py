class TestControl(ControlState):
    """Debugging control state."""
    def __init__(self):
        ControlState.__init__(self)
        self.keymap = {"printA": "a",
                       "left": "arrow_left",
                       "up": "arrow_up",
                       "right": "arrow_right",
                       "down": "arrow_down",
                       }
        self.fuctionmap = {"printA": self.printA}
        self.tasks = (self.printArrows)

    def printA(self):
        print "a pressed"

    def printArrows(self, task):
        """Print all requested actions, if any."""
        if self.requested_actions:
            print "pressed arrows: "+self.requested_actions
