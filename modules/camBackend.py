'''standard camera module, supporting multiple camera layouts'''

from errorHandler import *
from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

# View mode constants
FIRST_PERSON, COCKPIT, THIRD_PERSON, DETACHED = range(4)

class PlaneCamera():
	def __init__(self, parent, viewMode=THIRD_PERSON):
		self.camera = base.camera
		self.parent = parent		
		self.setViewMode(viewMode)
		
	def getViewMode(self):
		return self.__viewMode
		
	def setViewMode(self, viewMode):
		if viewMode == FIRST_PERSON:
			# plane specific - later on managable with emptys or config-vars.
			self.camera.reparentTo(self.parent)
			self.camera.setPos(-1.6, 3.3, 1.2)
			
		elif viewMode == COCKPIT:
			# plane specific - later on managable with emptys or config-vars.
			# buggy because of solid, one-sided textures.
			self.camera.reparentTo(self.parent)
			self.camera.setPosHpr(0, -1.5, 1.75, 0, 0, 0)

		elif viewMode == THIRD_PERSON:
			# should make use of aircraft bounds (see aeroplaneBackend)
			self.camera.reparentTo(self.parent)
			self.camera.setPosHpr(0, -25, 8, 0, -7, 0)
			
		elif viewMode == DETACHED:
			self.camera.reparentTo(render)
			self.camera.setPos(0, 0, 20)
			# rotation set by lookAt()
			
		else:
			raise ParamError("Expecting value of 0, 1, 2 or 3 in setViewMode()")
			
		self.__viewMode = viewMode
		
	def step(self):
		if self.__viewMode == DETACHED:
			self.camera.lookAt(self.parent)
			
	def rotate(self, direction):
		if self.__viewMode == THIRD_PERSON:
			dt = c.getDt()
			if direction == "move-left":
				self.camera.setH(self.camera, -5*dt)
			elif direction == "move-right":
				self.camera.setH(self.camera, 5*dt)
			elif direction == "move-origin":
				self.setViewMode(THIRD_PERSON)
			else:
				raise ParamError("Invalid value given for rotate(): %s" % direction)
