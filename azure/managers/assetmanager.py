from azure import assets
from azure.loader import Loader


class AssetManager(object):
    """An asset manager loads asset classes on demand, initializes them and
    keeps references to all of them. Main reason for this class is a central
    list of all assets depending on a context (e.g. a particular scenario).
    """
    def __init__(self, root):
        """Arguments:
        root -- path to the top node this manager assigns everything (NodePath)
        """
        # TODO: Set up a log notifier
        self.root = root
        self.assets = []
        self.loader = Loader()

    def load(self, asset, name, *args, **kwargs):
        """Loads an asset from the assets package and initialises it.
        Returns the asset instance on success or raises an Exception otherwise.
        
        Arguments:
        asset -- a class name from the assets package
        name -- a string that is used to identify this asset
        All other arguments will be passed to the constructor of the asset.
        """
        # Alternative that would save us from the garbage in __init__.py:
        # asset_module = __import__(asset.lower(), fromlist=["assets"])
        # getattr(asset_module, asset)

        if asset in dir(assets):
            A = getattr(assets, asset)
            a = A(name, *args, **kwargs)
            self.assets.append(a)
            return a
        else:
            raise Exception("Couldn't load asset: {} {}".format(asset, name))

    def get(self, name):
        """Returns a list of assets matching name."""
        result = []
        for a in self.assets:
            if a.name == name:
                result.append(a)
        return result

    def destroy(self):
        """Destroys all assets and removes the root node. This makes an
        instance of AssetManager unusable!"""
        for a in self.assets:
            a.destroy()
        self.assets = []
        self.root.removeNode()
        self.root = None
    
    def __repr__(self):
        r="AssetManager for root {}:".format(self.root)
        for a in self.assets:
            r+="\n\t{}   {}".format(type(a).__name__, a.name)
        return r
