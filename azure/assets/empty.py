from panda3d.core import NodePath

class Empty(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.node = NodePath(name)

    def destroy(self):
        self.node.removeNode()
        self.node = None
