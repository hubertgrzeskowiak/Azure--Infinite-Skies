'''this module manages everthing for scenery objects'''
'''very similar to the aeroplane class at writing of this comment 
1-29-08
'''

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

class scenery():

	scenery_count = 0

	def __init__(self, name, model_to_load=None, location=(0,0,0), size=None):
		new_node_name = "scenery" + str(scenery.scenery_count)
		self.dummy_node = render.attachNewNode(new_node_name)
		self.name = name
		self.scenery_model = None

		if not model_to_load:
			self.loadSceneModel(name)
		elif model_to_load == 0:
			pass
		else:
			self.loadSceneModel(model_to_load)

		self.place(location)
		if size != None:
			self.scale(size)

		# Maybe needs a collision variable to indicate result upon collision
		# with it 

	def loadSceneModel(self, model, force=False):
		if self.scenery_model != None:
			if force:
				self.scenery_model = loader.loadModel(model)
				self.scenery_model.reparentTo(self.dummy_node)
			else:
				print 'scenery already has a model. force to change'
				return 1
		else:
			self.scenery_model = loader.loadModel(model)
			self.scenery_model.reparentTo(self.dummy_node)

	def place(self, location):
		#sets the location of the scenery
		self.dummy_node.setX(location[0])
		self.dummy_node.setY(location[1])
		self.dummy_node.setZ(location[2])

	def scale(self, size):
		#changes the size of the scenery, good to make things look random
		self.dummy_node.setScale(size)
