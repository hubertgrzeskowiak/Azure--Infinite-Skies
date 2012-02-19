from panda3d.core import AmbientLight as AL, DirectionalLight as DL
from panda3d.core import Vec3, Vec4
from panda3d.core import NodePath

from assetbase import AssetBase

class AmbientLight(AssetBase):
    def __init__(self, name="ambient light", color=Vec4(0.6, 0.6, 0.8, 1)):
        self.light = AL("ambient light")
        self.light.setColor(color)
        self.node = NodePath(self.light)

class DirectionalLight(AssetBase):
    def __init__(self, name="directional light", color=Vec4(1,1,1,1)):
        self.light = DL("directional light")
        self.light.setColor(color)
        self.node = NodePath(self.light)

class DefaultLights(AssetBase):
    def __init__(self, name="default light"):
        self.ambient = AmbientLight()
        self.sun = DirectionalLight()


# Test
if __name__ == "__main__":
    a = AmbientLight()
    print a
    d = DirectionalLight()
    print d
