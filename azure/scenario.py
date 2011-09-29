class Scenario(object):
    """Abstract class for scenarios.

    A scenario can do the following:
    -preload (assets)
      This is done implicitly. Derived classes have to define what to preload
      in lists.
    -prepare
      Optional explicit preparations that need multiple frames, implemented as
      generator.
    -begin
      Required explicit code part that describes a part of game.
    -end
      A derived class can end itself or be ended from outside (through core
      FSM). Scenario class implicitly cleans up after this.
    """
    # game-wide default
    loader = None

    def __init__(self):
        self.loader = Scenario.loader  # later replaced with own implementation
        self._preloaded = 0  # number of preloaded assets

        # override in derived classes
        self.name = ""
        self.models = []
        self.fonts = []
        self.sounds = []
        # ...others

    @property
    def loadingprogress(self):
        """Return the progress of preloading assets (range 0.0 - 1.0)."""
        return self._preloaded / float(len(self.models))

    def _preload(self, task, async=False, atonce=False, force=False):
        """Implicitly preload 3d models, fonts and other assets.
        
        Arguments:
        async -- load asynchronously (in a new thread). this keeps the whole
                 program responsive
        atonce -- load all models at once, which is slightly faster, or one by
                  one, which can be used for better verbosity
        force -- load models even if the indicator says they already are.
                 this resets the loading progress var


        Possible combinations:
        async=False, atonce=True -- freeze everything and load as fast as possible
        async=False, atonce=False -- this is okay for less responsive loading
                                     screens
        async=True, atonce=True -- unresponsive background loading
        async=True, atonce=False -- responsive background loading e.g. for rich
                                    loading screens
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


    def prepare(self, task):
        """An abstract task/generator for time intensive precalculations."""
        # asynchronous tasks can be used here for managing time slices
        yield

    def begin(self):
        """Should run as fast as possible, so keep this simple. here you can
        set up assets, start animations, add tasks etc."""
        pass
