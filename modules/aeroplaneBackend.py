'''this module manages everthing around loading, setting and moving aircrafts'''

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

import ConfigParser
specs = ConfigParser.SafeConfigParser()
specs.read('etc/CraftSpecs.cfg')

from errorHandler import *

# container for everything flying around
aircrafts_cont = render.attachNewNode('aircrafts_cont')

class Aeroplane():
	'''standard aeroplane class.
	arguments:	name			-aircraft name
				model_to_load	-model to load on init. same as name if none
								given. 0 = don't load a model
				specs_to_load	-specifications to load on init. same as
								name if none given, 0 = don't load specs

	examples:	# load a craft called "corsair1" with model and specs "corsair"
				pirate1 = Aeroplane('corsair1', 'corsair')
				# load an empty craft instance (you'll have to load model and
				# specs later in turn to see or fly it)
				foo = Aeroplane('myname', 0, 0)
				# for the node itself, use:
				foo = Aeroplane('bar').dummy_node
				# if you need access to the model itself, use:
				foo = Aeroplane('bar').plane_model
	
	info:		invisible planes are for tracking only. you should assign them
				at least models	when they get into visible-range.
	'''
	
	plane_count = 0

	def __init__(self, name, model_to_load=None, specs_to_load=None):
		self.index = Aeroplane.plane_count
		Aeroplane.plane_count += 1

		new_node_name = 'dummy_node' + str(Aeroplane.plane_count)
		self.dummy_node = aircrafts_cont.attachNewNode(new_node_name)

		if model_to_load == 0:
			pass
		elif model_to_load:
			try:
				self.loadPlaneModel(model_to_load)
			except (ResourceHandleError, ResourceLoadError), e:
				handleError(e)
		else:
			try:
				self.loadPlaneModel(name)
			except (ResourceHandleError, ResourceLoadError), e:
				handleError(e)

		if specs_to_load == 0:
			pass
		elif specs_to_load:
			self.loadSpecs(specs_to_load)
		else:
			self.loadSpecs(name)

	def loadPlaneModel(self, model, force=False):
		'''loads model for a plane. force if there's already one loaded'''
		if hasattr(self, 'plane_model'):
			if force:
				self.plane_model = loader.loadModel(model)
				if self.plane_model != None:
					self.plane_model.reparentTo(self.dummy_node)
				else:
					raise ResourceLoadError(model, 'no such model')
			else:
				raise ResourceHandleError(model, 'aeroplane already has a model. force to change')
		else:
			self.plane_model = loader.loadModel(model)
			if self.plane_model:
				self.plane_model.reparentTo(self.dummy_node)
			else:
				raise ResourceLoadError(model, 'no such model')

	def loadSpecs(self, s, force=False):
		'''loads specifications for a plane. force if already loaded'''
		def justLoad():
			self.mass = specs.getint(s, 'mass')
			# 1km/h = 2.7777 m/s (1meter = 1panda unit)
			self.max_speed = 2.7777 * specs.getint(s, 'max_speed')
			self.roll_speed = specs.getint(s, 'roll_speed')
			self.pitch_speed = specs.getint(s, 'pitch_speed')
			self.yaw_speed = specs.getint(s, 'yaw_speed')

		if hasattr(self, 'specs'):
			if force:
				justLoad()
			else:
				print 'craft already has specs assigned. force to change'
			self.specs = s
		else:
			justLoad()

	def move(self, movement):
		dt = c.getDt()

		# TODO: physical correct slackness. this part requires some physical
		# correct forces and acceleration functions! don't touch it, as it has
		# to be fully rewritten anyway. feel free to do _that_ :)

		if movement == 'roll-left':
			self.dummy_node.setR(self.dummy_node, -1 * self.roll_speed * dt)
		if movement == 'roll-right':
			self.dummy_node.setR(self.dummy_node, self.roll_speed * dt)
		if movement == 'pitch-up':
			self.dummy_node.setP(self.dummy_node, self.pitch_speed * dt)
		if movement == 'pitch-down':
			self.dummy_node.setP(self.dummy_node, -1 * self.pitch_speed * dt)
		if movement == 'heap-left':
			self.dummy_node.setH(self.dummy_node, -1 * self.yaw_speed * dt)
		if movement == 'heap-right':
			self.dummy_node.setH(self.dummy_node, self.yaw_speed * dt)
		if movement == 'move-forward':
			# 40pu/s = ~12,4km/h
			self.dummy_node.setFluidY(self.dummy_node, 40 * dt)

	def getBounds(self):
		'''returns a vector describing the vehicle's size (width, length,
		height). useful for collision detection'''
		bounds = self.dummy_node.getTightBounds()
		size = bounds[1] - bounds[0]
		return size
