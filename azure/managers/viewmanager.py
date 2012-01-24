# IDEA: We could set up a second camera and give that to a second view
# on transition. This of course only makes sense where we need a transition
# with both views at the same time. The second camera with its buffer would be
# deleted right after the transition finished.

from direct.fsm import FSM

from azure import views


class ViewManager(FSM):
    """A view manager holds instances of view classes that control
    cameras. There is only one active view at a time.

    Although the attributes are not declared as private, this class is meant to
    be used only through its functions.
    """
    def __init__(self, camera):
        """Arguments:
        camera -- NodePath to the camera used
        """
        # TODO: Set up a log notifier
        FSM.__init__(self, "view manager")
        self.camera = camera
        self.view = None

    def setView(self, view, *args, **kwargs):
        """Set a view from views package.
        Arguments:
        view -- name of a view class from the views package
        All other arguments will be passed to the constructor of the view.
        """
        # First, remove the old view
        if self.view is not None:
            self.view.destroy()
        if view in dir(views):
            V = getattr(views, view)
            v = V(self.camera, *args, **kwargs)
        else:
            raise Exception("Couldn't load view: {}".format(view))

    def getView(self):
        """Get the currently active view class."""
        return self.view

    def getViewName(self):
        """Get the name of the currently active view class."""
        if hasattr(self.view, "__class__"):
            return self.view.__class__.__name__
        else:
            return None

    def destroy(self):
        """Destroy the active view and clean up this manager. This only resets
        the manager to its initial state, so it's safe (but unrecommended) to
        use it after calling this function.
        """
        self.view.destroy()
        self.view = None
