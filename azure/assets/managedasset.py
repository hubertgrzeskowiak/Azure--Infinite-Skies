from assetbase import AssetBase

class ManagedAsset(AssetBase):
    """A managed asset is a flexible way of defining a singleton. For each
    category there can only be one asset of that kind at the same time.
    If you declare two assets as "managed assets" by inheriting from this
    class with the same category, the first will be destroyed.
    """
    assets = {}
    
    def __init__(self, category):
        AssetBase.__init__(self)
        if category in ManagedAsset.assets:
            if "destroy" in dir(ManagedAsset.assets[category]):
                ManagedAsset.assets[category].destroy()
            ManagedAsset.assets[category] = self

    def destroy(self):
        super(ManagedAsset, self).destroy()
        
    @classmethod
    def getCategories(cls):
        return cls.assets.keys()
