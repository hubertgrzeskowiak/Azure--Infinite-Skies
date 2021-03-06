"""Loader module: contains the Loader class"""

__all__ = ['Loader']

import types

from panda3d.core import VBase4
from panda3d.core import LoaderOptions
from panda3d.core import Filename
from panda3d.core import NodePath
from panda3d.core import Loader as PandaLoader
from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.showbase.DirectObject import DirectObject

class Loader(DirectObject):
    """Loader for various stuff with asynchronous loading support
    for models.
    For textures, shaders etc. use the TexturePool, ShaderPool etc.
    """
    notify = directNotify.newCategory("Loader")
    loaderIndex = 0
    
    class Callback:
        def __init__(self, numObjects, gotList, callback, extraArgs):
            self.objects = [None] * numObjects
            self.gotList = gotList
            self.callback = callback
            self.extraArgs = extraArgs
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

    def __init__(self):
        self.loader = PandaLoader.getGlobalPtr()

        self.hook = "async loader %s" % (Loader.loaderIndex)
        Loader.loaderIndex += 1
        self.accept(self.hook, self.__gotAsyncObject)

    def destroy(self):
        self.ignore(self.hook)
        self.loader.stopThreads()
        del self.loader

    # model loading funcs
    def loadModel(self, modelPath, loaderOptions = None, noCache = None,
                  allowInstance = False, okMissing = None,
                  callback = None, extraArgs = [], priority = None):
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
            
            cb = Loader.Callback(len(modelList), gotList, callback, extraArgs)
            i=0
            for modelPath in modelList:
                request = self.loader.makeAsyncRequest(Filename(modelPath), loaderOptions)
                if priority is not None:
                    request.setPriority(priority)
                request.setDoneEvent(self.hook)
                request.setPythonObject((cb, i))
                i+=1
                self.loader.loadAsync(request)
                cb.requests[request] = True
            return cb

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

    def unloadModel(self, model):
        """
        model is the return value of loadModel().
        """
        if isinstance(model, NodePath):
            modelNode = model.node()

        elif isinstance(model, ModelNode):
            modelNode = model

        else:
            raise 'Invalid parameter to unloadModel: %s' % (model)

        assert Loader.notify.debug("Unloading model: %s" % (modelNode.getFullpath()))
        ModelPool.releaseModel(modelNode)


        
    def loadSound(self, manager, soundPath, positional = False,
                  callback = None, extraArgs = []):

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
            
            cb = Loader.Callback(len(soundList), gotList, callback, extraArgs)
            for i in range(len(soundList)):
                soundPath = soundList[i]
                request = AudioLoadRequest(manager, soundPath, positional)
                request.setDoneEvent(self.hook)
                request.setPythonObject((cb, i))
                self.loader.loadAsync(request)
                cb.requests[request] = True
            return cb


    def asyncFlattenStrong(self, model, inPlace = True,
                           callback = None, extraArgs = []):
        """ Performs a model.flattenStrong() operation in a sub-thread
        (if threading is compiled into Panda).  The model may be a
        single NodePath, or it may be a list of NodePaths.

        Each model is duplicated and flattened in the sub-thread.

        If inPlace is True, then when the flatten operation completes,
        the newly flattened copies are automatically dropped into the
        scene graph, in place the original models.

        If a callback is specified, then it is called after the
        operation is finished, receiving the flattened model (or a
        list of flattened models)."""
        
        if isinstance(model, NodePath):
            # We were given a single model.
            modelList = [model]
            gotList = False
        else:
            # Assume we were given a list of models.
            modelList = model
            gotList = True

        if inPlace:
            extraArgs = [gotList, callback, modelList, extraArgs]
            callback = self.__asyncFlattenDone
            gotList = True

        cb = Loader.Callback(len(modelList), gotList, callback, extraArgs)
        i=0
        for model in modelList:
            request = ModelFlattenRequest(model.node())
            request.setDoneEvent(self.hook)
            request.setPythonObject((cb, i))
            i+=1
            self.loader.loadAsync(request)
            cb.requests[request] = True
        return cb

    def __asyncFlattenDone(self, models, 
                           gotList, callback, origModelList, extraArgs):
        """ The asynchronous flatten operation has completed; quietly
        drop in the new models. """
        self.notify.debug("asyncFlattenDone: %s" % (models,))
        assert(len(models) == len(origModelList))
        for i in range(len(models)):
            origModelList[i].getChildren().detach()
            orig = origModelList[i].node()
            flat = models[i].node()
            orig.copyAllProperties(flat)
            orig.replaceNode(flat)

        if callback:
            if gotList:
                callback(origModelList, *extraArgs)
            else:
                callback(*(origModelList + extraArgs))

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
