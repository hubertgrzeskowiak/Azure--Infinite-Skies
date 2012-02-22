from panda3d.core import Filename
from panda3d.core import getModelPath
from panda3d.core import TextureStage, TexGenAttrib

from azure.errors import ResourceLoadError
from managedasset import ManagedAsset
from azure.loaderglobal import loader

class Sky(ManagedAsset):
    """A cube with a sky texture that always renders to background.
    
    Skies are implemented in form of a cube with 6 square textures. See
    resources/skyboxes/README.txt for more details.
    """
    def __init__(self, name, resource):
        """Arguments:
        resource -- name of a directory in assets/skyboxes that contains 6
        images.
        """
        ManagedAsset.__init__(self, "sky")
        self.name = name

        tex = None
        for ext in ("png", "jpg", "tga"):
            f = Filename("skyboxes/{}/0.{}".format(resource, ext))
            if f.resolveFilename(getModelPath().getValue()):
                tex = loader.loadCubeMap("skyboxes/{}/#.{}".format(resource, ext))
                break

        if tex is None:
            raise ResourceLoadError("assets/skyboxes/%s" % resource,
                                 "maybe wrong names or different extensions?")
        
        self.node = loader.loadModel("misc/invcube")
        self.node.clearTexture()
        self.node.clearMaterial()
        self.node.setScale(10000)
        self.node.setTwoSided(True)
        self.node.setBin('background', 0)
        self.node.setDepthTest(False)
        self.node.setDepthWrite(False)
        self.node.setLightOff()
        self.node.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.node.setTexProjector(TextureStage.getDefault(), render, self.node);
        self.node.setTexture(tex, 1)
        self.node.flattenLight()
        #self.node.setCompass()  # not needed with world-space-UVs
        self.addTask(self.update, "sky repositioning", sort=10,
                     taskChain="world")

    def update(self, task):
        self.node.setPos(camera.getPos(render))
        return task.cont
