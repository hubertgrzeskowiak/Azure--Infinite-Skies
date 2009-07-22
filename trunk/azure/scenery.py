"""This module manages everthing for scenery objects."""

from pandac.PandaModules import VBase3

from errors import *

# container for all scenery objects
scenery_cont = render.attachNewNode("scenery_cont")

class Scenery():
    """Standard scenery class."""

    scenery_count = 0

    def __init__(self, name, model_to_load=None, pos=VBase3(0,0,0), scale=VBase3(1,1,1)):
        """Arguments are model to load, position (default is parent's origin)
        and scale (default is 1)"""
        new_node_name = "Scenery" + str(Scenery.scenery_count)
        self.dummy_node = scenery_cont.attachNewNode(new_node_name)
        self.name = name
        if model_to_load == 0:
            pass
        elif model_to_load:
            try:
                self.loadSceneryModel(model_to_load)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)
        else:
            try:
                self.loadSceneryModel(name)
            except (ResourceHandleError, ResourceLoadError), e:
                handleError(e)
                
        self.node().setPos(pos)
        self.node().setScale(scale)

    def loadSceneryModel(self, model, force=False):
        """Loads a model for the scenery object. Force if there's already one
        loaded."""
        if hasattr(self, "scenery_model"):
            if force:
                self.scenery_model = loader.loadModel(model)
                if self.scenery_model != None:
                    self.scenery_model.reparentTo(self.node())
                else:
                    raise ResourceLoadError(model, "no such model")
            else:
                raise ResourceHandleError(model,
                    "scenery object already has a model. force to change")
        else:
            self.scenery_model = loader.loadModel(model)
            if self.scenery_model != None:
                self.scenery_model.reparentTo(self.node())
            else:
                raise ResourceLoadError(model, 'no such model')
    def node(self):
        """Returns a container class, which you should use instead of
        dummy_mode or the model itself."""
        return self.dummy_node
