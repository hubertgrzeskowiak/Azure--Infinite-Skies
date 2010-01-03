"""Camera(s) handling module"""

import string

from direct.fsm.FSM import FSM
#from pandac.PandaModules import ClockObject
from pandac.PandaModules import NodePathCollection, NodePath
from direct.directnotify.DirectNotify import DirectNotify
from direct.task import Task

from errors import *
from aircrafts import Aeroplane


# View mode constants
FIRST_PERSON, COCKPIT, THIRD_PERSON, DETACHED = range(4)

class PlaneCamera(FSM):
    """Give this class a plane as argument and it will create
    some nodes around it which you can parent the camera to (if there are no
    such nodes yet). Keep in mind, that it only uses base.camera the whole
    time - no other cams are involved.

    Usage:
    plane_camera = PlaneCamera(aeroplane)
    plane_camera.setCameraMode("ThirdPerson")
    plane_camera.setCameraMode("Next")
    """
    def __init__(self, parent):
        """Arguments:
        parent -- Aeroplane which the camera should follow
        """

        # Used for debugging. Verbosity is set in config file.
        # Usually this is called self.notify, but in this case it would
        # override FSM's own.
        self.notifier = DirectNotify().newCategory("azure-camera")
        self.parent = parent
        # Replaced by a NodePath with all available cameras as children and
        # plane node as parent.
        self.__cameras = None

        #if parent.__class__.__name__ is not "Aeroplane":
        if not isinstance(self.parent, Aeroplane):
            raise ParamError, "Parent must be an Aeroplane instance, but is %s" % type(self.parent)

        FSM.__init__(self, "PlaneCamera: %s" % self.parent.name)

        try:
            self.camera = base.camera
        except:
            raise BaseMissing

        self.__cameras = self.parent.node.find("cameras")
        if self.__cameras.isEmpty():
            self.createCamNodes()
        self.updateCamArray()

        # Set up the default camera
        self.setCameraMode("ThirdPerson")

    def createCamNodes(self):
        """Creates a few empty nodes around a plane which the camera might be
        parented to. It looks if there are cameras inside the model file and
        uses those if possible. Where everything named "camera CamType" is
        considered a camera. At least ThirdPerson, FirstPerson and Cockpit
        should be defined inside the egg file, otherwise some guessed defaults
        are taken.
        """

        # Look for cameras inside the model (loaded egg file)
        cameras = NodePath("cameras")
        _c = self.parent.node.findAllMatches("**/camera ?*")
        _c.removeDuplicatePaths()
        _c.reparentTo(cameras)

        if not cameras.isEmpty():
            self.notifier.info("Cameras found under model:\n%s"
                               % _c)
        else:
            self.notifier.info("No cameras found under model.")

        # FirstPerson camera is a must-have. Set up a guessed one if none
        # defined yet.
        if not cameras.find("camera FirstPerson"):
            assert self.notifier.debug("No first person camera found in %s. "
                                  "Guessing best position." % self.parent.name)
            first_person = NodePath("camera FirstPerson")
            # TODO: Guess best position based on bounding box.
            first_person.setY(5)
            first_person.reparentTo(cameras)

        # ThirdPerson camera is a must-have. Set up a guessed one if none
        # defined yet.
        if not cameras.find("camera ThirdPerson"):
            assert self.notifier.debug("No third person camera found in %s. "
                                  "Guessing best position." % self.parent.name)
            third_person = NodePath("camera ThirdPerson")
            # TODO: Guess best position based on bounding box.
            third_person.setPos(0, -20, 3)
            third_person.setP(-80)
            third_person.reparentTo(cameras)

        # Cockpit needs to be accurate. Don't try to guess it.
        if not cameras.find("camera Cockpit"):
            assert self.notifier.debug("No cockpit camera found in "
                                       "%s. Cockpit camera disabled."
                                       % self.parent.name)

        self.__cameras = cameras
        # Store the cams at parent node..
        # You can edit the camera nodes from outside as well.
        # If you attach new camera nodes, though, you'll have to call this
        # function again.
        cameras.reparentTo(self.parent.node)

    def updateCamArray(self, cameramodes=None):
        """Set the cameras which next and previous will switch to. Expects a
        list or tuple. Defaults to all available cameras."""
        a = []
        if not cameramodes:
            for c in self.__cameras.getChildren():
                if c.getName().startswith("camera "):
                    a.append(c.getName().strip("camera "))
            self.setStateArray(a)
        else:
            self.setStateArray(cameramodes)


    def getCameraMode(self):
        """Returns the current view mode."""
        return self.getCurrentOrNextState()

    def setCameraMode(self, mode, *args):
        """Convenience function."""
        return self.request(mode, args)

    def defaultEnter(self, *args):
        """Executed by the FSM every time an undefined state is entered.
        Note: this function is called AFTER the responsible filter."""

        assert self.notifier.debug("Changing state from %s to %s with args: %s."
                                   % (self.oldState, self.newState, args))
        request = self.newState

        target_cam = self.__cameras.find("camera " + request)
        if target_cam:
            try:
                self.camera.reparentTo(target_cam)
                self.camera.setPosHpr(0, 0, 0, 0, 0, 0)
            except:
                self.notifier.warning(
                        "Ok, now this really shouldn't happen! Filter said the"
                        "camera is there and enter can't find it...")



    def defaultFilter(self, request, args):
        """Executed by the FSM every time an undefined state is requested."""
        assert self.notifier.debug("Requested %s with args: %s"
                                   % (request, args))
        if request == "Off":
            return (request,) + args
        if request == "Next":
            return self.requestNext(args)
        if request == "Prev":
            return self.requestPrev(args)
        if request == "Detached":
            return (request,) + args
        if request == "Sideview":
            return (request,) + args
        if self.__cameras.find("camera " + request):
            # TODO(Nemesis13, 26.10.09): add some nice camera transition
            return (request,) + args
        assert self.notifier.info("Sorry, no %s camera found." % request)
        return None


    def enterOff(self, *args):
        """Clean up everything by reparenting the camera to the plane."""
        self.camera.reparentTo(self.parent.node)
        self.camera.setPosHpr(0, 0, 0, 0, 0, 0)

    def requestNext(self, *args):
        """Request the 'next' state in the predefined state array."""
        self.fsmLock.acquire()
        try:
            if self.stateArray is not []:
                if not self.state in self.stateArray:
                    self.request(self.stateArray[0])
                else:
                    cur_index = self.stateArray.index(self.state)
                    new_index = (cur_index + 1) % len(self.stateArray)
                    self.request(self.stateArray[new_index], args)
            else:
                assert self.notifier.debug(
                                    "stateArray empty. Can't switch to next.")

        finally:
            self.fsmLock.release()

    def requestPrev(self, *args):
        """Request the 'previous' state in the predefined state array."""
        self.fsmLock.acquire()
        try:
            if self.stateArray is not []:
                if not self.state in self.stateArray:
                    self.request(self.stateArray[0])
                else:
                    cur_index = self.stateArray.index(self.state)
                    new_index = (cur_index - 1) % len(self.stateArray)
                    self.request(self.stateArray[new_index], args)
            else:
                assert self.notifier.debug(
                                    "stateArray empty. Can't switch to next.")
        finally:
            self.fsmLock.release()

    # Extra States:

    def enterSideview(self, *args):
        taskMgr.add(self.__sideView, "sideview camera")
        #self.camera.reparentTo(self.parent.node)
        self.camera.reparentTo(render)
        self.camera.setPos(0, 0, 0)
        self.camera.setHpr(-90 ,0, 0)
        #if "fixed rotation" in args:
        #    if self.sideview != "fixed rotation":

    def exitSideview(self, *args):
        taskMgr.remove("sideview camera")

    def __sideView(self, task):
        #self.camera.setY(self.parent.node)
        #self.camera.setX(self.parent.node.getX(render) -30)
        self.camera.setPos(self.parent.node.getX() -30, self.parent.node.getY(), self.parent.node.getZ())
        #self.camera.setPos(self.parent.node.getX() -30,
        #        self.parent.node.getY(), self.parent.node.getZ())
        #self.camera.lookAt(self.parent.node)
        #print self.parent.node.getPos(), self.parent.node.getHpr()


        return Task.cont


    def enterDetached(self, *args):
        """Lets the camera view the plane from far away."""
        self.camera.reparentTo(render)
        self.camera.setPosHpr(0, 0, 0, 0, 0, 0)
        taskMgr.add(self.__detachedCam, "detached camera")

    def exitDetached(self, *args):
        taskMgr.remove("detached camera")

    def __detachedCam(self, task):
        """Updates camera position and rotation for Detached camera."""
        try:
            self.camera.lookAt(self.parent.node)
        except:
            assert self.notifier.warning("Error on detached cam task. Exit.")
            return Task.done
        return Task.cont

    def enterThirdPerson(self, *args):
        """Lets the camera view the plane from far away."""
        target_cam = self.__cameras.find("camera ThirdPerson")
        if target_cam:
            try:
                self.camera.reparentTo(target_cam)
                self.camera.setPosHpr(0, 0, 0, 0, 0, 0)
            except:
                self.notifier.warning(
                        "Ok, now this really shouldn't happen! Filter said the"
                        "camera is there and enter can't find it...")

        #taskMgr.add(self.__thirdPersonCam, "third person camera")

    def exitThirdPerson(self, *args):
        taskMgr.remove("third person camera")

    def __thirdPersonCam(self, task):
        """Updates camera position and rotation for ThirdPerson camera."""
        #speed = self.parent.speed()
        #camnode = self.__cameras.find("camera ThirdPerson")
        #par = self.parent.node
        #camnode.reparentTo(par)

        #camnode.lookAt(par, (0, (20 + speed/2), 0))
        #camnode.setY(-30 - speed/10)

        return Task.cont
