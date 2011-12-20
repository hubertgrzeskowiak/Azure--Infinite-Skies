from panda3d.core import NodePath

class AssetBase(object):
    """Classes for assets are considered proxies - mostly for models in the
    scene graph.
    """
    def __init__(self):
        """The constructor should only expect ultimately required parameters.
        """
        # Path to the root node.
        self.node = NodePath()

        # Name of the particular asset.
        self.name = "(No name given)"

        # Path to the actually visible node. Must be either the same as
        # self.node or a child of it. This is optional.
        self.model = NodePath("temporary asset node") # can be an Actor alternatively


    def destroy(self):
        """Cleans up everyting this asset created and attached to the SG.
        Override to add more sophisticated cleanup functionality."""
        self.node.removeNode()
