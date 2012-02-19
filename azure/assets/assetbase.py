from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject

class AssetBase(DirectObject):
    """Classes for assets are considered proxies - mostly for models in the
    scene graph.
    """
    def __init__(self):
        """The constructor should only expect ultimately required parameters.
        """
        # Path to the root node.
        self.node = NodePath("Asset Base")

        # Name of the particular asset.
        self.name = "(No name given)"

        # Path to the actually visible node (NodePath). Must be either the
        # same as self.node or a child of it.
        self.model = self.node

    def destroy(self):
        """Cleans up everyting this asset created and attached to the SG.
        Override to add more sophisticated cleanup functionality."""
        self.node.removeNode()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
