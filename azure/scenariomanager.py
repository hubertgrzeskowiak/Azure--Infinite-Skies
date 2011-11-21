from direct.fsm.FSM import FSM
from scenarioproxy import ScenarioProxy

class ScenarioManager(FSM):

    def __init__(self, top_root):
        FSM.__init__(self, "scenario manager")
        self.current = None

    def defaultEnter(self, request, args):
        s = ScenarioProxy(request)
        s.prepare()
        s.begin()
        self.current = s

    def defaultExit(self, args):
        self.scenario.destroy()
        self.scenario = None
