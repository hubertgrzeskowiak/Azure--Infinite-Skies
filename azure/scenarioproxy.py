import types

from azure.managers import AssetManager, ViewManager, ControlManager
from preloader import Preloader
from errors import ScenarioLoadingError

class Managers(object):
    """Dummy class we attach managers to."""
    pass

class ScenarioProxy(object):
    """Proxy for scenarios that adds a few methods and offers checks of a
    scenario. One Proxy is used for one scenario. This is the preffered way of
    accessing scenario classes.
    """
    def __init__(self, scenario):
        """Arguments:
        scenario -- a string that maps to a class name in the scenarios
                    directory, or a class object
        """
        if isinstance(scenario, types.StringTypes):
            import scenarios
            try:
                self.scenario = getattr(scenarios, scenario)()
            except AttributeError:
                raise ScenarioLoadingError(scenario)
        else:
            self.scenario = scenario()
        self.root = render.attachNewNode("scenario "+self.scenario.name)

        self.managers = Managers()
        self.managers.assets = AssetManager(self.root)
        self.managers.views = ViewManager(base.camera)
        self.managers.controls = ControlManager()
        # more to come

    def begin(self):
        self.scenario.begin(self.managers)

    def destroy(self):
        for m in self.managers:
            m.destroy()
