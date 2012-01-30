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
