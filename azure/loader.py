from pandac.PandaModules import *
from direct.directnotify.DirectNotifyGlobal import *
from direct.showbase.DirectObject import DirectObject
import types


class Loader(DirectObject):
    """Load assets from hard drive or cache."""
    notify = directNotify.newCategory("Loader")
    
    class Callback:
        def __init__(self, numObjects, gotList, callback):
            self.objects = [None] * numObjects
            self.gotList = gotList
            self.callback = callback
            self.numRemaining = numObjects
            self.cancelled = False
            self.requests = {}

        def gotObject(self, index, object):
            self.objects[index] = object
            self.numRemaining -= 1

            if self.numRemaining == 0:
                if self.gotList:
                    self.callback(self.objects, *self.extraArgs)
                else:
                    self.callback(*(self.objects + self.extraArgs))

    def cancelRequest(self, cb):
        """Cancels an aysynchronous loading or flatten request issued
        earlier.  The callback associated with the request will not be
        called after cancelRequest() has been performed. """
        
        if not cb.cancelled:
            cb.cancelled = True
            for request in cb.requests:
                self.loader.remove(request)
            cb.requests = None

    def isRequestPending(self, cb):
        """ Returns true if an asynchronous loading or flatten request
        issued earlier is still pending, or false if it has completed or
        been cancelled. """
        
        return bool(cb.requests)

    # special methods
    def __init__(self):
        self.loader = PandaLoader.getGlobalPtr()

    def destroy(self):
        self.loader.stopThreads()
        del self.loader

    # model loading funcs
    def loadModel(self, modelPath, loaderOptions = None, noCache = None,
                  allowInstance = False, okMissing = None,
                  callback = None, priority = None):
        """
        Attempts to load a model or models from one or more relative
        pathnames.  If the input modelPath is a string (a single model
        pathname), the return value will be a NodePath to the model
        loaded if the load was successful, or None otherwise.  If the
        input modelPath is a list of pathnames, the return value will
        be a list of NodePaths and/or Nones.

        loaderOptions may optionally be passed in to control details
        about the way the model is searched and loaded.  See the
        LoaderOptions class for more.

        The default is to look in the ModelPool (RAM) cache first, and
        return a copy from that if the model can be found there.  If
        the bam cache is enabled (via the model-cache-dir config
        variable), then that will be consulted next, and if both
        caches fail, the file will be loaded from disk.  If noCache is
        True, then neither cache will be consulted or updated.

        If allowInstance is True, a shared instance may be returned
        from the ModelPool.  This is dangerous, since it is easy to
        accidentally modify the shared instance, and invalidate future
        load attempts of the same model.  Normally, you should leave
        allowInstance set to False, which will always return a unique
        copy.

        If okMissing is True, None is returned if the model is not
        found or cannot be read, and no error message is printed.
        Otherwise, an IOError is raised if the model is not found or
        cannot be read (similar to attempting to open a nonexistent
        file).  (If modelPath is a list of filenames, then IOError is
        raised if *any* of the models could not be loaded.)

        If callback is not None, then the model load will be performed
        asynchronously.  In this case, loadModel() will initiate a
        background load and return immediately.  The return value will
        be an object that may later be passed to
        loader.cancelRequest() to cancel the asynchronous request.  At
        some later point, when the requested model(s) have finished
        loading, the callback function will be invoked with the n
        loaded models passed as its parameter list.  It is possible
        that the callback will be invoked immediately, even before
        loadModel() returns.  If you use callback, you may also
        specify a priority, which specifies the relative importance
        over this model over all of the other asynchronous load
        requests (higher numbers are loaded first).

        True asynchronous model loading requires Panda to have been
        compiled with threading support enabled (you can test
        Thread.isThreadingSupported()).  In the absence of threading
        support, the asynchronous interface still exists and still
        behaves exactly as described, except that loadModel() might
        not return immediately.
        
        """
        
        assert Loader.notify.debug("Loading model: %s" % (modelPath))
        if loaderOptions == None:
            loaderOptions = LoaderOptions()
        else:
            loaderOptions = LoaderOptions(loaderOptions)

        if okMissing is not None:
            if okMissing:
                loaderOptions.setFlags(loaderOptions.getFlags() & ~LoaderOptions.LFReportErrors)
            else:
                loaderOptions.setFlags(loaderOptions.getFlags() | LoaderOptions.LFReportErrors)
        else:
            okMissing = ((loaderOptions.getFlags() & LoaderOptions.LFReportErrors) == 0)

        if noCache is not None:
            if noCache:
                loaderOptions.setFlags(loaderOptions.getFlags() | LoaderOptions.LFNoCache)
            else:
                loaderOptions.setFlags(loaderOptions.getFlags() & ~LoaderOptions.LFNoCache)

        if allowInstance:
            loaderOptions.setFlags(loaderOptions.getFlags() | LoaderOptions.LFAllowInstance)

        if isinstance(modelPath, types.StringTypes) or \
           isinstance(modelPath, Filename):
            # We were given a single model pathname.
            modelList = [modelPath]
            gotList = False
        else:
            # Assume we were given a list of model pathnames.
            modelList = modelPath
            gotList = True
        
        if callback is None:
            # We got no callback, so it's a synchronous load.

            result = []
            for modelPath in modelList:                
                node = self.loader.loadSync(Filename(modelPath), loaderOptions)
                if (node != None):
                    nodePath = NodePath(node)
                else:
                    nodePath = None

                result.append(nodePath)

            if not okMissing and None in result:
                message = 'Could not load model file(s): %s' % (modelList,)
                raise IOError, message

            if gotList:
                return result
            else:
                return result[0]

        else:
            # We got a callback, so we want an asynchronous (threaded)
            # load.  We'll return immediately, but when all of the
            # requested models have been loaded, we'll invoke the
            # callback (passing it the models on the parameter list).
            
            cb = Loader.Callback(len(modelList), gotList, callback)
            i=0
            for modelPath in modelList:
                request = self.loader.makeAsyncRequest(Filename(modelPath), loaderOptions)
                if priority is not None:
                    request.setPriority(priority)
                request.setPythonObject((cb, i))
                i+=1
                self.loader.loadAsync(request)
                cb.requests[request] = True
            return cb


    def loadFont(self, modelPath, okMissing = False):
        assert Loader.notify.debug("Loading font: %s" % (modelPath))

        font = FontPool.loadFont(modelPath)
        if font == None:
            if not okMissing:
                message = 'Could not load font file: %s' % (modelPath)
                raise IOError, message
            # If we couldn't load the model, at least return an
            # empty font.
            font = StaticTextFont(PandaNode("empty"))
        return font

    def loadTexture(self, texturePath, alphaPath = None,
                    readMipmaps = False, okMissing = False,
                    minfilter = None, magfilter = None, anisotropicDegree = None):
        """
        texturePath is a string.

        Attempt to load a texture from the given file path using
        TexturePool class.

        okMissing should be True to indicate the method should return
        None if the texture file is not found.  If it is False, the
        method will raise an exception if the texture file is not
        found or cannot be loaded.

        If alphaPath is not None, it is the name of a grayscale image
        that is applied as the texture's alpha channel.

        If readMipmaps is True, then the filename string must contain
        a sequence of hash characters ('#') that are filled in with
        the mipmap index number, and n images will be loaded
        individually which define the n mipmap levels of the texture.
        The base level is mipmap level 0, and this defines the size of
        the texture and the number of expected mipmap images.

        If minfilter or magfilter is not None, they should be a symbol
        like Texture.FTLinear or Texture.FTNearest.  (minfilter may be
        further one of the Mipmap filter type symbols.)  These specify
        the filter mode that will automatically be applied to the
        texture when it is loaded.  Note that this setting may
        override the texture's existing settings, even if it has
        already been loaded.  See egg-texture-cards for a more robust
        way to apply per-texture filter types and settings.

        If anisotropicDegree is not None, it specifies the anisotropic degree
        to apply to the texture when it is loaded.  Like minfilter and
        magfilter, egg-texture-cards may be a more robust way to apply
        this setting.
        """
        if alphaPath is None:
            assert Loader.notify.debug("Loading texture: %s" % (texturePath))
            texture = TexturePool.loadTexture(texturePath, 0, readMipmaps)
        else:
            assert Loader.notify.debug("Loading texture: %s %s" % (texturePath, alphaPath))
            texture = TexturePool.loadTexture(texturePath, alphaPath, 0, 0, readMipmaps)
        if not texture and not okMissing:
            message = 'Could not load texture: %s' % (texturePath)
            raise IOError, message

        if minfilter is not None:
            texture.setMinfilter(minfilter)
        if magfilter is not None:
            texture.setMagfilter(magfilter)
        if anisotropicDegree is not None:
            texture.setAnisotropicDegree(anisotropicDegree)
        
        return texture

    def load3DTexture(self, texturePattern, readMipmaps = False, okMissing = False,
                      minfilter = None, magfilter = None, anisotropicDegree = None):
        """
        texturePattern is a string that contains a sequence of one or
        more hash characters ('#'), which will be filled in with the
        z-height number.  Returns a 3-D Texture object, suitable for
        rendering volumetric textures.

        okMissing should be True to indicate the method should return
        None if the texture file is not found.  If it is False, the
        method will raise an exception if the texture file is not
        found or cannot be loaded.

        If readMipmaps is True, then the filename string must contain
        two sequences of hash characters; the first group is filled in
        with the z-height number, and the second group with the mipmap
        index number.
        """
        assert Loader.notify.debug("Loading 3-D texture: %s" % (texturePattern))
        texture = TexturePool.load3dTexture(texturePattern, readMipmaps)
        if not texture and not okMissing:
            message = 'Could not load 3-D texture: %s' % (texturePattern)
            raise IOError, message

        if minfilter is not None:
            texture.setMinfilter(minfilter)
        if magfilter is not None:
            texture.setMagfilter(magfilter)
        if anisotropicDegree is not None:
            texture.setAnisotropicDegree(anisotropicDegree)

        return texture

    def loadCubeMap(self, texturePattern, readMipmaps = False, okMissing = False,
                    minfilter = None, magfilter = None, anisotropicDegree = None):
        """
        texturePattern is a string that contains a sequence of one or
        more hash characters ('#'), which will be filled in with the
        face index number (0 through 6).  Returns a six-face cube map
        Texture object.

        okMissing should be True to indicate the method should return
        None if the texture file is not found.  If it is False, the
        method will raise an exception if the texture file is not
        found or cannot be loaded.

        If readMipmaps is True, then the filename string must contain
        two sequences of hash characters; the first group is filled in
        with the face index number, and the second group with the
        mipmap index number.
        """
        assert Loader.notify.debug("Loading cube map: %s" % (texturePattern))
        texture = TexturePool.loadCubeMap(texturePattern, readMipmaps)
        if not texture and not okMissing:
            message = 'Could not load cube map: %s' % (texturePattern)
            raise IOError, message

        if minfilter is not None:
            texture.setMinfilter(minfilter)
        if magfilter is not None:
            texture.setMagfilter(magfilter)
        if anisotropicDegree is not None:
            texture.setAnisotropicDegree(anisotropicDegree)

        return texture

        
    def loadSound(self, manager, soundPath, positional = False,
                  callback = None):

        """Loads one or more sound files, specifying the particular
        AudioManager that should be used to load them.  The soundPath
        may be either a single filename, or a list of filenames.  If a
        callback is specified, the loading happens in the background,
        just as in loadModel(); otherwise, the loading happens before
        loadSound() returns."""
    
        if isinstance(soundPath, types.StringTypes) or \
           isinstance(soundPath, Filename):
            # We were given a single sound pathname.
            soundList = [soundPath]
            gotList = False
        elif isinstance(soundPath, MovieAudio):
            soundList = [soundPath]
            gotList = False
        else:
            # Assume we were given a list of sound pathnames.
            soundList = soundPath
            gotList = True

        if callback is None:
            # We got no callback, so it's a synchronous load.

            result = []
            for soundPath in soundList:
                # should return a valid sound obj even if musicMgr is invalid
                sound = manager.getSound(soundPath)
                result.append(sound)

            if gotList:
                return result
            else:
                return result[0]

        else:
            # We got a callback, so we want an asynchronous (threaded)
            # load.  We'll return immediately, but when all of the
            # requested sounds have been loaded, we'll invoke the
            # callback (passing it the sounds on the parameter list).
            
            cb = Loader.Callback(len(soundList), gotList, callback)
            for i in range(len(soundList)):
                soundPath = soundList[i]
                request = AudioLoadRequest(manager, soundPath, positional)
                request.setPythonObject((cb, i))
                self.loader.loadAsync(request)
                cb.requests[request] = True
            return cb

    def loadShader (self, shaderPath, okMissing = False):
        shader = ShaderPool.loadShader (shaderPath)
        if not shader and not okMissing:
            message = 'Could not shader file: %s' % (shaderPath)
            raise IOError, message
        return shader

    def unloadShader(self, shaderPath):
        if (shaderPath != None):
            ShaderPool.releaseShader(shaderPath)


    def __gotAsyncObject(self, request):
        """A model or sound file or some such thing has just been
        loaded asynchronously by the sub-thread.  Add it to the list
        of loaded objects, and call the appropriate callback when it's
        time."""

        cb, i = request.getPythonObject()
        if cb.cancelled:
            return

        del cb.requests[request]

        object = None
        if hasattr(request, "getModel"):
            node = request.getModel()
            if (node != None):
                object = NodePath(node)

        elif hasattr(request, "getSound"):
            object = request.getSound()

        cb.gotObject(i, object)
