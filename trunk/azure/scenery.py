"""This module manages everthing for scenery objects."""

from pandac.PandaModules import VBase3
from pandac.PandaModules import CardMaker
from pandac.PandaModules import GeomNode
from pandac.PandaModules import NodePath

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

    def id(self):
        """Every scenery object has its own unique ID."""
        return self._id

    def node(self):
        """Returns a container class, which you should use instead of
        dummy_mode or the model itself."""
        return self._dummy_node


def setSky(directory, ext=".jpg"):
    """Sets up a skybox. 'directory' is the directory whitch contains 6
    pictures with the names right.ext, left.ext and so on (see template).
    ext is the extension the pictures have (with dot).
    """
    #TODO: accept all supported image file extensions without the need for an
    #      extra argument

    # remove the old sky first when loading a new one
    # TODO: get this working...
    #oldsky = render.find("*sky*")
    #print oldsky
    #for child in render.getChildren():
    #    child.remove()

    sky = NodePath().attachNewNode("sky")
    sides = {
        "right":  ( 1,  0,  0, -90,   0,  0),
        "left":   (-1,  0,  0,  90,   0,  0),
        "top":    ( 0,  0,  1,   0,  90,  0),
        "bottom": ( 0,  0, -1,  180,  -90,  0),
        "front":  ( 0,  1,  0,   0,   0,  0),
        "back":   ( 0, -1,  0, 180,   0,  0)
        }
    for name, poshpr in sides.iteritems():

        c = CardMaker(name)
        c.setFrame(-1, 1, -1, 1)
        card = c.generate()
        cardnode = sky.attachNewNode(card)
        cardnode.setPosHpr(*poshpr)
        tex = loader.loadTexture("skyboxes/" + directory + "/" + name + ext)
        tex.setWrapV(tex.WMClamp)
        tex.setMagfilter(tex.FTNearestMipmapNearest)
        tex.setMinfilter(tex.FTNearestMipmapNearest)
        cardnode.setTexture(tex)

    sky.flattenStrong()
    sky.setScale(10, 10, 10)
    sky.setCompass()
    sky.setBin('background', 0)
    sky.setDepthTest(False)
    sky.setDepthWrite(False)
    sky.setLightOff()
    sky.reparentTo(camera)

    geom = sky.getChild(0).node()
    geom.setName("cube")


    # doesn't work yet. no idea why

    #from pandac.PandaModules import MultitexReducer as MR
    #MR.scan(sky)
    #MR.flatten()

    #geom.unify(1, False)
    #print geom.getNumGeoms()

    #def myprint(arg):
    #    print arg
    #base.accept("f1", myprint, [sky])
    #base.accept("f2", myprint, [sky.getChildren()])
    #base.accept("f3", render.ls)
