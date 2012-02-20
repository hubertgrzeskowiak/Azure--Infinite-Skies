from panda3d.core import NodePath

from assetbase import AssetBase

class Empty(AssetBase):
    def __init__(self, name):
        AssetBase.__init__(self)
        self.name = name
        self.node = NodePath(name)

    def destroy(self):
        self.node.removeNode()
