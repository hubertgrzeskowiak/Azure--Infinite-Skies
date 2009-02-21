"""Camera(s) handling module"""

from errorHandler import *
from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

# View mode constants
FIRST_PERSON, COCKPIT, THIRD_PERSON, DETACHED = range(4)

class PlaneCamera():
    """Player's plane camera management"""

    def __init__(self, parent, view_mode=THIRD_PERSON):
        """Arguments are object to which the camera should be parented to
        and the view mode. latter defaults to THIRD_PERSON"""

        self.camera = base.camera
        self.parent = parent        
        self.setViewMode(view_mode)
        
    def getViewMode(self):
        """Returns the current view mode"""

        return self.__view_mode
        
    def setViewMode(self, view_mode):
        """Sets camera view mode. Takes a view_mode constant as argument."""
        if view_mode == FIRST_PERSON:
            # plane specific - later on managable with emptys or config-vars.
            self.camera.reparentTo(self.parent)
            self.camera.setPos(-1.6, 3.3, 1.2)
            
        elif view_mode == COCKPIT:
            # plane specific - later on managable with emptys or config-vars.
            # buggy because of solid, one-sided textures.
            self.camera.reparentTo(self.parent)
            self.camera.setPosHpr(0, -1.5, 1.75, 0, 0, 0)

        elif view_mode == THIRD_PERSON:
            # should make use of aircraft bounds (see aeroplaneBackend)
            self.camera.reparentTo(self.parent)
            self.camera.setPosHpr(0, -25, 8, 0, -7, 0)
            
        elif view_mode == DETACHED:
            self.camera.reparentTo(render)
            self.camera.setPos(0, 0, 20)
            # rotation set by lookAt()
            
        else:
            raise ParamError("Expecting value of 0, 1, 2 or 3 in setViewMode()")
            
        self.__view_mode = view_mode
        
    def step(self):
        """In DETACHED camera mode, rotates the camera to look at parent
        (player)"""
        if self.__view_mode == DETACHED:
            self.camera.lookAt(self.parent)
            
    def rotate(self, direction):
        """In THIRD_PERSON camera mode, rotates camera to side. Parameter is
        direction"""
        if self.__view_mode == THIRD_PERSON:
            dt = c.getDt()
            if direction == "move-left":
                self.camera.setH(self.camera, -5*dt)
            elif direction == "move-right":
                self.camera.setH(self.camera, 5*dt)
            elif direction == "move-origin":
                self.setViewMode(THIRD_PERSON)
            else:
                raise ParamError("Invalid value given for rotate(): %s" % direction)
