from errorHandler import *

# View mode constants
DETACHED, FIRST_PERSON, THIRD_PERSON = range(3)

class planeCamera():
	def __init__(self, parent, viewMode=THIRD_PERSON):
		self.camera = base.cam
		self.parent = parent		
		self.setViewMode(viewMode)
		
	def getViewMode(self):
		return self.__viewMode
		
	def setViewMode(self, viewMode):
		if viewMode == FIRST_PERSON:
			self.camera.reparentTo(self.parent)
			self.camera.setHpr(0, 0, 0)
			self.camera.setPos(5, 0, 0)
			
		elif viewMode == THIRD_PERSON:
			self.camera.reparentTo(self.parent)
			self.camera.setHpr(0, -16, 0)
			self.camera.setPos(0, -25, 12)
			
		elif viewMode == DETACHED:
			self.camera.reparentTo(render)
			self.camera.setHpr(0, -16, 0)
			self.camera.setPos(0, -25, 12)
			
		else:
			raise ParamError("Expecting value of 0, 1, or 2 in setViewMode()")
			
		self.__viewMode = viewMode
		
	def step(self):
		if self.__viewMode == DETACHED:
			self.camera.lookAt(self.parent)
		else:
			pass
			
	def rotate(self, direction):
		if self.__viewMode == THIRD_PERSON:
			if direction == "move-left":
				self.camera.setHpr(self.camera, -5, 0, 0)
			elif direction == "move-right":
				self.camera.setHpr(self.camera, 5, 0, 0)
			elif direction == "move-origin":
				self.setViewMode(THIRD_PERSON)
			else:
				raise ParamError("Invalid value given for rotate(): %s" % direction)
