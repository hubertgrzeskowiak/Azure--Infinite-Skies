from direct.task import Task

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
