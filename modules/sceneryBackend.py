'''this module manages everthing for scenery objects'''

from pandac.PandaModules import VBase3

# container for all scenery objects
scenery_cont = render.attachNewNode('scenery_cont')

class scenery():
	'''syntax similar to aeroplaneBackend'''

	scenery_count = 0

	def __init__(self, name, model_to_load=None, pos=VBase3(0,0,0), scale=VBase3(1,1,1)):
		new_node_name = 'scenery' + str(scenery.scenery_count)
		self.dummy_node = scenery_cont.attachNewNode(new_node_name)
		self.name = name
		if model_to_load == 0:
			pass
		elif model_to_load:
			self.loadSceneryModel(model_to_load)
		else:
			self.loadSceneryModel(name)
		self.dummy_node.setPos(pos)
		self.dummy_node.setScale(scale)

	def loadSceneryModel(self, model, force=False):
		'''loads a model for the scenery object. force if there's already one
		loaded'''
		if hasattr(self, 'scenery_model'):
			if force:
				self.scenery_model = loader.loadModel(model)
				if self.scenery_model != None:
					self.scenery_model.reparentTo(self.dummy_node)
				else:
					print 'no such model:', model
			else:
				print 'scenery object already has a model. force to change'
		else:
			self.scenery_model = loader.loadModel(model)
			if self.scenery_model:
				self.scenery_model.reparentTo(self.dummy_node)
			else:
				print 'no such model:', model
