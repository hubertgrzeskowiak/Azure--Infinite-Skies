from direct.gui.DirectGui import *

class PauseMenu(object):
    """Simple ingame menu that's shown when pause is requested."""
    def __init__(self):
        self.dialog = OkDialog(fadeScreen=0.5, text="Game Paused")
        self.dialog.show()

    def destroy(self):
        self.dialog.destroy()
