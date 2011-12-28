"""Camera(s) handling module"""

import string

from direct.fsm.FSM import FSM
#from pandac.PandaModules import ClockObject
from pandac.PandaModules import NodePathCollection, NodePath, Vec3, Point3, LineSegs
from direct.directnotify.DirectNotify import DirectNotify
from direct.task import Task
from direct.showbase.DirectObject import DirectObject

from errors import *
from aircrafts import Aeroplane


class PlaneCamera(FSM, DirectObject):
    """Give this class a plane as argument and it will create
    some nodes around it which you can parent the camera to (if there are no
    such nodes yet). Keep in mind, that it only uses base.camera the whole
    time - no other cams are involved.

    Usage:
    plane_camera = PlaneCamera(aeroplane)
    plane_camera.setView("ThirdPerson")
    plane_camera.setView("Next")
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
        self.cameras = None

        #if parent.__class__.__name__ is not "Aeroplane":
        if not isinstance(self.parent, Aeroplane):
            raise ParamError, "Parent must be an Aeroplane instance, " + \
                              "but is %s" % type(self.parent)

        FSM.__init__(self, "PlaneCamera: %s" % self.parent.name)
        DirectObject.__init__(self)

        try:
            self.camera = base.camera
        except:
            raise BaseMissing

        self.cameras = self.parent.node.find("cameras")
        if self.cameras.isEmpty():
            self.createCamNodes()
        self.updateCamArray()

        self.sideview_direction = 0

        # Set up the default camera
        self.setView("ThirdPerson")

    def createCamNodes(self):
        """Creates a few empty nodes around a plane which the camera might be
        parented to. It looks if there are cameras inside the model file and
        uses those if possible. Where everything named "camera CamType" is
        considered a camera. At least ThirdPerson, FirstPerson and Cockpit
        should be defined inside the egg file, otherwise some guessed defaults
        are taken.
        """

        # Look for cameras inside the model (loaded egg file)
        self.cameras = NodePath("cameras")
        found_cams = self.parent.node.findAllMatches("**/camera ?*")
        found_cams.removeDuplicatePaths()
        found_cams.reparentTo(self.cameras)

        if not found_cams.isEmpty():
            self.notifier.info("Cameras found under model:\n%s"
                               % found_cams)
        else:
            self.notifier.info("No cameras found under model.")

        # FirstPerson camera is a must-have. Set up a guessed one if none
        # defined yet.
        if self.cameras.find("camera FirstPerson").isEmpty():
            assert self.notifier.debug("No first person camera found in %s. "
                                  "Guessing best position." % self.parent.name)
            first_person = NodePath("camera FirstPerson")
            # TODO: Guess best position based on bounding box.
            first_person.setY(5)
            first_person.reparentTo(cameras)

        # ThirdPerson camera is a must-have. Set up a guessed one if none
        # defined yet.
        if self.cameras.find("camera ThirdPerson").isEmpty():
            assert self.notifier.debug("No third person camera found in %s. "
                                  "Guessing best position." % self.parent.name)
            third_person = NodePath("camera ThirdPerson")
            # TODO: Guess best position based on bounding box.
            third_person.setPos(0, -30, 5)
            #third_person.setP(-80)
            third_person.reparentTo(cameras)

        # Cockpit needs to be accurate. Don't try to guess it.
        if self.cameras.find("camera Cockpit").isEmpty():
            assert self.notifier.debug("No cockpit camera found in "
                                       "%s. Cockpit camera disabled."
                                       % self.parent.name)
        self.sideview_cam = NodePath("camera Sideview")
        self.sideview_cam.reparentTo(render)

        # Store the cams at parent node..
        # You can edit the camera nodes from outside as well.
        # If you attach new camera nodes, though, you'll have to call this
        # function again.
        self.cameras.reparentTo(self.parent.node)

    def updateCamArray(self, cameramodes=None):
        """Set the cameras which next and previous will switch to. Expects a
        list or tuple. Defaults to all available cameras."""
        a = []
        if not cameramodes:
            for c in self.cameras.getChildren():
                if c.getName().startswith("camera "):
                    a.append(c.getName().strip("camera "))
            self.setStateArray(a)
        else:
            self.setStateArray(cameramodes)

    def getView(self):
        """Returns the current view mode."""
        return self.getCurrentOrNextState()

    def setView(self, mode, *args):
        """Convenience function."""
        return self.request(mode, args)

    def defaultEnter(self, *args):
        """Executed by the FSM every time an undefined state is entered.
        Note: this function is called AFTER the responsible filter."""

        assert self.notifier.debug("Changing state from %s to %s with args: %s."
                                   % (self.oldState, self.newState, args))
        request = self.newState

        target_cam = self.cameras.find("camera " + request)
        if not target_cam.isEmpty():
            try:
                self.camera.reparentTo(target_cam)
                self.camera.setPosHpr(0, 0, 0, 0, 0, 0)
            except:
                self.notifier.warning(
                        "Ok, now this really shouldn't happen! Filter said the "
                        "camera is there and enter can't find it...")



    def defaultFilter(self, request, args):
        """Executed by the FSM every time an undefined state is requested."""
        assert self.notifier.debug("Requested %s with args: %s"
                                   % (request, args))

        self.camera.setPosHpr(0, 0, 0, 0, 0, 0)

        # Always available.
        if request == "Off":   # implemented in FSM.py
            return (request,) + args
        if request == "Next":  # implemented in FSM.py
            return self.requestNext(args)
        if request == "Prev":  # implemented in FSM.py
            return self.requestPrev(args)
        if request == "Detached":
            return (request,) + args
        if request == "Sideview":
            return (request,) + args
        
        # Depending on airplane.
        if not self.cameras.find("camera " + request).isEmpty():
            # TODO(Nemesis13, 26.10.09): add some nice camera transition
            return (request,) + args
        assert self.notifier.info("Sorry, no %s camera found." % request)
        return None


    def enterOff(self, *args):
        """Clean up everything by reparenting the camera to the airplane."""
        self.camera.reparentTo(self.parent.node)
        self.camera.setPosHpr(0, 0, 0, 0, 0, 0)

    def enterSideview(self, *args):
        self.sideview_direction += 90
        self.camera.reparentTo(self.sideview_cam)
        self.camera.setY(-30)
        self.sideview_cam.setH(self.sideview_direction)
        self.addTask(self.updateSideview, "sideview camera", taskChain="world")

    def exitSideview(self, *args):
        self.removeTask("sideview camera")

    def updateSideview(self, task):
        self.sideview_cam.setPos(self.parent.node.getPos())
        return Task.cont

    def enterDetached(self, *args):
        """Lets the camera view the plane from far away."""
        self.camera.reparentTo(render)
        self.camera.setPosHpr(0, 0, 10, 0, 0, 0)
        self.addTask(self.updateDetachedCam, "detached camera",
                     taskChain="world")

    def exitDetached(self, *args):
        self.removeTask("detached camera")

    def updateDetachedCam(self, task):
        """Updates camera position and rotation for Detached camera."""
        try:
            self.camera.lookAt(self.parent.node)
        except:
            self.notifier.warning("Error on detached cam task. Exit.")
            return Task.done
        return Task.cont

    def enterThirdPerson(self, *args):
        """Lets the camera view the plane from far away."""
        self._hist = []
        self.camera.reparentTo(self.cameras.find("camera ThirdPerson"))
        self.cameras.find("camera ThirdPerson").setPos(0, -30, 0)
        self.addTask(self.updateThirdPersonCam, "third person camera",
                     taskChain="world")
        #print "entering third person"

    def exitThirdPerson(self, *args):
        self.removeTask("third person camera")
        del self._hist
        #print "third person exited"

    def updateThirdPersonCam(self, task):
        """Updates camera position and rotation for ThirdPerson camera."""
        speed = self.parent.physics.speed()
        velocity = self.parent.physics.velocity()
        #v = Point3(self.parent.physics.angVelVector())
        v = Point3(self.parent.physics.angVelBodyHpr())
        print round(v.getX(), 2), round(v.getY(), 2), round(v.getZ(), 2)

        #self.segs = LineSegs("lines");
        #self.segs.setColor(1,1,1,1)
        #self.segs.drawTo(-1, 0)
        #self.segsnode = self.segs.create()
        #render2d.attachNewNode(self.segsnode) 

        vec = Point3(self.parent.physics.angVelBodyHpr())
        # Y hiervon ist pitch, Z ist roll
        #print round(vec.getY(), 2), round(vec.getZ(), 2)
        self.camera.lookAt(self.parent.node)
        self.camera.setR(self.camera, vec.getZ()*3)
        #self.camera.setPos(abs(v.getX()), 0,  vec.getY())

        

        #plane = self.parent.node
        #self._hist.insert(0, [task.time, camera.getPos(plane)])
        #while len(self._hist) > 50:
        #    self._hist.pop()
        #
        #for snapshot in self._hist:
        #    if snapshot[0] > task.time:
        #        break
        #time_delta = snapshot[0] - task.time
        #self.camera.setPos(plane, snapshot[1])

        #print snapshot
        #self.camera.setPos(render, snapshot[1])
        #self.camera.lookAt(plane, (0, 20+1*speed, 0))

        #self.camera.setY(5+0.1*speed)
        #self.camera.setZ(5-0.1*speed)

        return Task.cont

    def destroy(self):
        self.removeAllTasks()
        self.demand("Off")
