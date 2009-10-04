"""Camera(s) handling module"""

from pandac.PandaModules import ClockObject
from direct.directnotify.DirectNotify import DirectNotify
from direct.task import Task
from errors import *

c = ClockObject.getGlobalClock()

# View mode constants
FIRST_PERSON, COCKPIT, THIRD_PERSON, DETACHED = range(4)

class PlaneCamera(object):
    """Player's plane camera management"""

    def __init__(self, parent, view_mode=THIRD_PERSON):
        """Arguments:
        parent -- object which the camera should follow
        view_mode -- available modes are FIRST_PERSON, COCKPIT, THIRD_PERSON
                     and DETACHED. THIRD_PERSON is default. modes are
                     importable from this module"""
        
        self.notify = DirectNotify().newCategory("azure-camera")
        assert base
        self.camera = base.camera
        self.parent = parent        
        self.setViewMode(view_mode)
        
    def getViewMode(self):
        """Returns the current view mode"""
        try:
            return self.__view_mode
        except:
            return None
        
    def setViewMode(self, view_mode):
        """Sets camera view mode. Takes a view_mode constant as argument."""

        if view_mode != self.getViewMode():
            self.notify.info("setting view to %s" % view_mode)
        else:
            self.notify.info("view already is %s. doing nothing" % view_mode)
            return

        if view_mode == FIRST_PERSON:
            # plane specific - later on managable with emptys or config-vars.
            self.camera.reparentTo(self.parent)
            self.camera.setPosHpr(-1.6, 3.3, 1.2, 0, -7, 0)
            
        elif view_mode == COCKPIT:
            # plane specific - later on managable with emptys or config-vars.
            # buggy because of solid, one-sided textures.
            self.camera.reparentTo(self.parent)
            self.camera.setPosHpr(0, -1.5, 1.75, 0, 0, 0)

        elif view_mode == THIRD_PERSON:
            # should make use of aircraft bounds (see aircrafts.py)
            self.camera.reparentTo(self.parent)
            self.camera.setPosHpr(0, -25, 8, 0, -7, 0)
            
        elif view_mode == DETACHED:
            self.camera.reparentTo(render)
            self.camera.setPos(0, 0, 20)
            # rotation set by lookAt()
            
        else:
            self.notify.warning("%s view mode unknown" % view_mode)
            raise ParamError("Unknown Option: %s" % view_mode)
            
        self.__view_mode = view_mode
        
    def _update_cam(self, task):
        """updates camera position and rotation"""
        if self.__view_mode == DETACHED:
            self.camera.lookAt(self.parent)
