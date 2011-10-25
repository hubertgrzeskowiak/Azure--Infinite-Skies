from panda3d.core import PandaLoader, TexturePool, FontPool
# PandaLoader is the new ModelPool - kind of

class Preloader(Directobject):
    def __init__(self, models=[], fonts=[], sounds=[], textures=[],
                 textures3d=[], cubemaps=[]):

        self.models = models
        self.fonts = fonts
        self.sounds = sounds
        self.textures = textures
        self.textures3d = textures3d
        self.cubemaps = cubemaps

        self.modelloader = PandaLoader.getGlobalPtr().loadModel
        l = PandaLoader.getGlobalPtr()
        self.asyncmodelloader = lambda x: l.loadAsync(l.makeAsyncRequest(x))
        self.textureloader = TexturePool.loadTexture
        self.fontloader = FontPool.loadFont

        self._preloaded = 0

    @property
    def progress(self):
        """Return the progress of preloading assets (range 0.0 - 1.0)."""
        return self._preloaded / float(len(self.models)+
                                       len(self.fonts)+
                                       len(self.sounds)+
                                       len(self.textures)+
                                       len(self.textures3d)+
                                       len(self.cubemaps)
                                       )

    def preloadFast(self):
        """Load everything NOW."""
        return self.preload(async=False, atonce=True)

    def preloadPerFrame(self):
        """Every frame one asset is loaded. Frames might last long."""
        return self.addTask(self.preload, "preloading",
                            extraArgs={async=False, atonce=False})

    def preloadBackground(self):
        """Progress indicator will jump after each batch."""
        return self.addTask(self.preload, "preloading",
                            extraArgs={async:True, atonce:True})

    def preloadBackgroundResponsive(self):
        """Progress indicator will raise after each loaded asset."""
        return self.addTask(self.preload, "preloading",
                            extraArgs={async:True, atonce:False})

    def preload(self, task=None, async=False, atonce=False, force=False):
        """Implicitly preload 3d models, fonts and other assets.
        
        Arguments:
        task -- when using async, this function is passed to a task manager.
                this arg will be filled by a task manager in such a case
        async -- load asynchronously (in a new thread). this keeps the whole
                 program responsive
        atonce -- load all models at once, which is slightly faster, or one by
                  one, which can be used for better verbosity
        force -- load models even if the indicator says they already are.
                 this resets the loading progress var
        """
        # TODO: preload not only models, but also other assets

        if self.loadingprogress == 1:
            if force:
                self._preloaded = 0
            else:
                return

        def setStatus(*args):
            print args
            self._preloaded += len(args)

        if async:
            if atonce:
                self.loader.loadModel(self.models, callback=setStatus)
            else:
                for model in self.models:
                    self.loader.loadModel(model, callback=setStatus)
                    yield
        else:
            if atonce:
                setStatus(self.loader.loadModel(self.models))
            else:
                for model in self.models:
                    setStatus(self.loader.loadModel(model))
                    yield
