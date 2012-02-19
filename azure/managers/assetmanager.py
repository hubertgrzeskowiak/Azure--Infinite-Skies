from azure import assets
from azure.loader import Loader
from azure.errors import ResourceLoadError


class AssetManager(object):
    """An asset manager loads asset classes on demand, initializes them and
    keeps references to all of them. Main reason for this class is a central
    list of all assets depending on a context (e.g. a particular scenario).

    Although the attributes are not declared as private, this class is meant to
    be used only through its functions.
    """
    def __init__(self, root):
        """Arguments:
        root -- path to the top node this manager assigns everything (NodePath)
        """
        # TODO: Set up a log notifier
        self.root = root
        self.assets = []
        self.loader = Loader()

    def add(self, asset, name="asset", *args, **kwargs):
        """Load an asset from the assets package and initialise it.
        Return an id on success or raises an Exception otherwise.
        
        Arguments:
        asset -- a class name from the assets package
        name -- a string that is used to identify this asset (doesn't have to
                be unique)
        All other arguments will be passed to the constructor of the asset.
        """
        # Alternative that would save us from the garbage in assets/__init__.py:
        # asset_module = __import__(asset.lower(), fromlist=["assets"])
        # getattr(asset_module, asset)

        if asset not in dir(assets):
            raise ResourceLoadError(asset, name)

        cls = getattr(assets, asset)
        obj = cls(name, *args, **kwargs)
        obj.node.reparentTo(self.root)
        self.assets.append(obj)
        return len(self.assets)-1

    def getByName(self, name):
        """Return a list of assets matching name."""
        return [a for a in self.assets if a.name == name]

    def getById(self, id):
        """Return one asset that is identified by id."""
        return self.assets[id]

    def getLast(self):
        """Return the most recently added asset."""
        return self.assets[len(self.assets)-1]

    def deleteAsset(self, id):
        """Destroy an asset completely. Remove it from from the scene
        graph and from this manager. The id won't be recycled."""
        self.assets[id].destroy()
        self.assets[id] = None

    def destroy(self):
        """Destroy all assets and removes the root node. This makes an
        instance of AssetManager unusable!"""
        for a in self.assets:
            a.destroy()
        self.assets = []
        self.root = None
    
    def __repr__(self):
        r="AssetManager for root {}:".format(self.root)
        for a in self.assets:
            r+="\n\t{}   {}".format(type(a).__name__, a.name)
        return r


# Test
# Needs assets.empty.Empty
if __name__ == "__main__":
    from panda3d.core import NodePath

    root = NodePath("root")
    am = AssetManager(root)
    id0 = am.add("Empty", "empty test asset 1")
    id1 = am.add("Empty", "empty test asset 2")
    assert id0 == 0 and id1 == 1
    assert am.getById(id1).__class__.__name__ == "Empty"
    assert am.getById(id0) == am.getByName("empty test asset 1")[0]
    am.destroy()
    assert len(am.assets) == 0
    assert root.getChildren().getNumPaths() == 0
