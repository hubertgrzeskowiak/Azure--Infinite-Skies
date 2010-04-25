"""Azure's core FSM."""

from pandac.PandaModules import OdeWorld

from direct.fsm.FSM import FSM
from direct.gui.OnscreenText import OnscreenText
from pandac.PandaModules import TextNode

import scenarios
from scenarios import Scenario
import gui

class Core(FSM):
    def __init__(self):
        FSM.__init__(self, "Core Game Control")
        self.defaultTransitions = {"Menu": ["World"],
                                   "World": ["Pause"],
                                   "Pause": ["World", "Menu"]}
        self.demand("Menu")

    def enterWorld(self, scenario=scenarios.TestEnvironment):
        #self.world = OdeWorld()
        #self.world.setGravity(0.0, 0.0, 0.0)
        #world.setGravity(0.0, 0.0, -9.81)
        loading = OnscreenText(text="LOADING", pos=(0,0), scale=0.1,
                               align=TextNode.ACenter, fg=(1,1,1,1))
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
        self.scenario = scenario()
        loading.destroy()
        self.scenario.start()

    def exitWorld(self):
        self.world.destroy()  # Muharharhar *evil laugh*

    
    def enterMenu(self, menu=gui.MainMenu):
        self.menu = menu()

    def exitMenu(self):
        self.menu.destroy()


    def defaultFilter(self, request, args):
        if request not in self.defaultTransitions:
            if type(request).__name__ == "type":
                # It's a class.
                if request in scenarios.Scenario.list():
                    return ("World",) + request
            elif isinstance(request, basestring):
                if not request.startswith("scenarios."):
                    request = "scenarios." + request
                if request in scenarios.Scenario.names():
                    return ("World",) + eval("scenarios." + request)
        else:
            return request
