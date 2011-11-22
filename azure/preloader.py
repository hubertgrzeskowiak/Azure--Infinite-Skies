# TODO look at AsyncTask and PandaLoader, which seem to load everything

#from panda3d.core import PandaLoader, TexturePool, FontPool
# PandaLoader is the new ModelPool - kind of

from direct.showbase.DirectObject import DirectObject

def scenarioPreloader(scenario):
    """Create a preloader and attach values from a scenario file to it, then
    return it."""
    preloader = Preloader()
    s = scenario
    preloader.models = s.models if hasattr(s, "models") else []
    preloader.fonts = s.fonts if hasattr(s, "fonts") else []
    preloader.sounds = s.sounds if hasattr(s, "sounds") else []
    preloader.textures = s.textures if hasattr(s, "textures") else []
    preloader.textures3d = s.textures3d if hasattr(s, "textures3d") else []
    preloader.cubemaps = s.cubemaps if hasattr(s, "cubemaps") else []
    return preloader


class Preloader(DirectObject):
    def __init__(self, models=[], fonts=[], sounds=[], textures=[],
                 textures3d=[], cubemaps=[]):

        self.models = models
        self.fonts = fonts
        self.sounds = sounds
        self.textures = textures
        self.textures3d = textures3d
        self.cubemaps = cubemaps

        # TODO: replace with something more object oriented and not so.. global
        self.loader = base.loader

        self._preloaded = 0
        self._progress_cached = -1
        self._progress_f_cached = -1.0

    @property
    def progress(self):
        """Return the progress of preloading assets in percent (range 0 - 100).
        """
        # through the multiplication we save ourselves a floating point
        # division
        if self._progress_cached < 0:
            items_len = len(self.models)+\
                        len(self.fonts)+\
                        len(self.sounds)+\
                        len(self.textures)+\
                        len(self.textures3d)+\
                        len(self.cubemaps)
            if items_len != 0:
                result = self._preloaded  * 100 / items_len
            else:
                result = 0
            self._progress_cached = result
            return result
        else:
            return self._progress_cached

    @property
    def progressFloat(self):
        """Return the progress of preloading assets in percent
        (range 0.0 - 1.0). This is slightly slower than the upper function.
        """
        if self._progress_f_cached < 0:
            items_len = len(self.models)+\
                        len(self.fonts)+\
                        len(self.sounds)+\
                        len(self.textures)+\
                        len(self.textures3d)+\
                        len(self.cubemaps)
            if items_len != 0:
                result = self._preloaded / float(items_len)
            else:
                result = 0.0
            self._progress_f_cached = result
            return result
        else:
            return self._progress_f_cached

    # Convenience functions.
    def preloadFast(self, *args):
        """Load everything in one frame. This uses doMethodLater for loading in
        next frame, so wen can show a loading screen in the meanwhile."""
        return self.preload(async=False, atonce=True)

    def preloadPerFrame(self):
        """Every frame one asset is loaded. Frames might last long."""
        return self.addTask(self.preload, "preloading",
                            extraArgs={"async":False, "atonce":False})

    def preloadBackground(self, callback=None):
        """Progress indicator will jump after each batch.
        Arguments:
        callback -- a function to call upon finish
        """
        return self.addTask(self.preload, "preloading",
                            extraArgs={"async":True, "atonce":True})

    def preloadBackgroundResponsive(self, callback=None):
        """Progress indicator will raise after each loaded asset.
        Arguments:
        callback -- a function to call upon finish
        """
        return self.addTask(self.preload, "preloading",
                            extraArgs={"async":True, "atonce":False})


    def preload(self, task=None, async=False, atonce=False, force=False):
        """Preload 3d models, fonts and other assets that are assigned to self
        as lists.
        
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

        if self.progress == 1:
            if force:
                self._preloaded = 0
            else:
                return

        def setStatus(*args):
            self._progress_cached = -1
            self._progress_f_cached = -1.0
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
