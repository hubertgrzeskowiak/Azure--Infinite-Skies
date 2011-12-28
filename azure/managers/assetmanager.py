from azure import assets
from azure.loader import Loader


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

    def load(self, asset, name="asset", *args, **kwargs):
        """Loads an asset from the assets package and initialises it.
        Returns an id on success or raises an Exception otherwise.
        
        Arguments:
        asset -- a class name from the assets package
        name -- a string that is used to identify this asset (doesn't have to
                be unique)
        All other arguments will be passed to the constructor of the asset.
        """
        # Alternative that would save us from the garbage in __init__.py:
        # asset_module = __import__(asset.lower(), fromlist=["assets"])
        # getattr(asset_module, asset)

        if asset in dir(assets):
            A = getattr(assets, asset)
            a = A(name, self.loader, *args, **kwargs)
            self.assets.append(a)
            return len(self.assets)-1
        else:
            raise Exception("Couldn't load asset: {} {}".format(asset, name))

    def getByName(self, name):
        """Returns a list of assets matching name."""
        result = []
        for a in self.assets:
            if a.name == name:
                result.append(a)
        return result

    def getById(self, id):
        """Returns one asset that is identified by id."""
        return self.assets[id]

    def deleteAsset(self, id):
        """Destroys an asset completely. It removes it from from the scene
        graph and from this manager. The id won't be recycled."""
        self.assets[id].destroy()
        self.assets[id] = None

    def destroy(self):
        """Destroys all assets and removes the root node. This makes an
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
    id0 = am.load("Empty", "empty test asset 1")
    id1 = am.load("Empty", "empty test asset 2")
    assert id0 == 0 and id1 == 1
    assert am.getById(id1).__class__.__name__ == "Empty"
    assert am.getById(id0) == am.getByName("empty test asset 1")[0]
    am.destroy()
    assert len(am.assets) == 0
    assert root.getChildren().getNumPaths() == 0
