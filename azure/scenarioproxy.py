import types

from direct.showbase.Messenger import Messenger

from preloader import Preloader

class ScenarioProxy(object):
    """Proxy for scenarios that adds a few methods and offers checks of a
    scenario. One Proxy is used for one scenario. This is the preffered way of
    accessing scenario classes.
    """
    def __init__(self, scenario):
        """Arguments:
        scenario -- a string that maps to a class name in the scenarios
                    directory or class
        """
        if isinstance(scenario, types.StringTypes):
            import scenarios
            self.scenario = getattr(scenarios, scenario)()
        else:
            self.scenario = scenario()
        # TODO: get render-top-root here, somehow
        #self.root = root
        #self.assetloader = AssetLoader(self.root)
        #self.messenger = Messenger()
        # TODO: task manager?
        #self.taskmanager = ...?

    def begin(self):
        #self.scenario.begin(self.assetloader, self.messenger)
        self.scenario.begin()

    def destroy(self):
        pass
        # TODO.....
