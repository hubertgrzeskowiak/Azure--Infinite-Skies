"""Manager for control states."""

from azure import controls

class ControlManager(self):
    def __init__(self):
        self.controlstates = []

    def add(self, control, *args, **kwargs):
        C = getattr(controls, control)
        for c in self.controlstates:
            if c.__class__.__name__ == control and c.active:
                c.disable()
                print "WARNING! Disabling control state {} "
                      "because of collision.".format(str(c))
        self.controlstates.append(C(*args, **kwargs))

    def activate(self, id):
        self.controlstates[id].activate()

    def addAndActivate(self, control, *args, **kwargs):
        c = self.add(control, *args, **kwargs)
        c.activate()

    def disable(self, id):
        self.controlstates[id].disable()

    def getLast(self):
        return self.controlstates[len(self.controlstates-1)]

    def getById(self, id):
        return self.controlstates[id]

    def getByName(self, name):
        return [c for c in self.controlstates if c.__class__.__name__ == name]


# Test
if __name__ == "__main__":
    cm = ControlManager()
    cm.addAndActivate("TestControl")
