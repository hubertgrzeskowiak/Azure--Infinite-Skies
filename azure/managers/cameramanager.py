from azure import views


class CameraManager(object):
    """A camera manager holds instances of view classes that control
    cameras. By default there is only one active camera and this class assumes
    that only one camera is used. It is not usable for multi-camera views.

    Although the attributes are not declared as private, this class is meant to
    be used only through its functions.
    """
    def __init__(self, camera):
        """Arguments:
        camera -- NodePath to the camera used
        """
        # TODO: Set up a log notifier
        self.camera = camera
        self.active_view = None

    def setView(self, view, *args, **kwargs):
        """Set a view from views package.
        Arguments:
        view -- name of a view class from the views package
        All other arguments will be passed to the constructor of the view.
        """
        # First, remove the old view
        if self.active_view is not None:
            self.active_view.destroy()
        if view in dir(views):
            V = getattr(views, view)
            v = V(self.camera, *args, **kwargs)
        else:
            raise Exception("Couldn't load view: {}".format(view))

    def getView(self):
        return self.active_view

    def getViewName(self):

        if hasattr(self.active_view, "__class__"):
            return self.active_view.__class__.__name__
        else:
            return None

    def destroy(self):
        """Destroy the active view and clean up this manager. This only resets
        the manager to its initial state, so it's safe (but unrecommended) to
        use it after calling this function.
        """
        self.active_view.destroy()
        self.active_view = None
