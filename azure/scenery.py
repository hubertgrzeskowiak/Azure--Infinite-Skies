"""This module manages everthing about non-interactive environment."""

from pandac.PandaModules import *

from errors import *


class Scenery(object):
    """Standard scenery class."""

    _scenery_count = 0

    def __init__(self, name, model_to_load=None, pos=VBase3(0,0,0),
            scale=VBase3(1,1,1)):
        """Arguments are model to load, position (default is parent's origin)
        and scale (default is 1)"""

        if not hasattr(Scenery, "_scenery"):
            assert render
            _scenery = render.attachNewNode("scenery")

        self._id = Scenery._scenery_count
        Scenery._scenery_count += 1

        new_node_name = "Scenery" + str(Scenery._scenery_count)
        self._dummy_node = Scenery._scenery.attachNewNode(new_node_name)
        del new_node_name
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

        self.node.setPos(pos)
        self.node.setScale(scale)

    def loadSceneryModel(self, model, force=False):
        """Loads a model for the scenery object. Force if there's already one
        loaded."""
        if hasattr(self, "scenery_model"):
            if force:
                self.scenery_model = loader.loadModel(model)
                if self.scenery_model != None:
                    self.scenery_model.reparentTo(self.node)
                else:
                    raise ResourceLoadError(model, "no such model")
            else:
                raise ResourceHandleError(model,
                    "scenery object already has a model. force to change")
        else:
            self.scenery_model = loader.loadModel(model)
            if self.scenery_model != None:
                self.scenery_model.reparentTo(self.node)
            else:
                raise ResourceLoadError(model, 'no such model')

    def id(self):
        """Every scenery object has its own unique ID."""
        return self._id

    def node(self):
        """Returns a container class, which you should use instead of
        dummy_mode or the model itself."""
        return self._dummy_node


class Sky(NodePath):
    """Skies are implemented in form of a cube with 6 square textures. See
    assets/skyboxes/README.txt for more details."""
    def __init__(self, resource=None):
        if resource is not None:
            self.create(resource)
    def create(self, resource):
        """Arguments:
        resource -- name of a directory in assets/skyboxes that contains 6
        images."""
        for ext in ("png", "jpg", "tga"):
            f = "skyboxes/%s/0.%s" % (resource, ext)
            if vfs.resolveFilename(f, getModelPath().getValue()):
                tex = loader.loadCubeMap("skyboxes/%s/#.%s" % (resource, ext))
                if tex is not None:
                    break
        if tex is None:
            raise ResourceLoadError("assets/skyboxes/%s" % resource,
                                 "maybe wrong names or different extensions?")
        self = loader.loadModel("misc/invcube")
        self.clearTexture()
        self.clearMaterial()
        self.setScale(100)
        self.setTwoSided(True)
        self.setBin('background', 0)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setLightOff()
        self.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.setTexProjector(TextureStage.getDefault(), render, self);
        self.setTexture(tex, 1)
        self.setCompass()
        self.reparentTo(camera)
