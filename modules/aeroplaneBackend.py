'''this module manages everthing around loading, setting and moving aircrafts'''

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

import ConfigParser
specs = ConfigParser.SafeConfigParser()
specs.read('etc/CraftSpecs.cfg')


class aeroplane():
	'''standard aeroplane class.
	arguments:	name			-aircraft name
				model_to_load	-model to load on init. same as name if none
								given. 0 = don't load a model
				specs_to_load	-specifications to load on init. same as
								model_to_load if none given, 0 = don't load
								specs

	examples:	# load a craft called "corsair1" with model and specs "corsair"
				pirate1 = aeroplane("corsair1", "corsair")
				# load an empty craft instance (you'll have to load model and
				# specs later in turn to see or fly it)
				foo = aeroplane("myname", 0, 0)
				# for the node itself, use:
				foo = aeroplane("bar").dummy_node
				# if you need access to the model itself, use:
				foo = aeroplane("bar").plane_model
	
	info:		invisible planes are for tracking only. you should assign them
				at least models	when they get into visible-range.
	'''
	
	plane_count = 0

	def __init__(self, name, model_to_load=None, specs_to_load=None):
		self.index = aeroplane.plane_count
		aeroplane.plane_count += 1

		new_node_name = 'dummy_node' + str(aeroplane.plane_count)
		self.dummy_node = render.attachNewNode(new_node_name)
		
		if not model_to_load:
			self.loadPlaneModel(name)
		elif model_to_load == 0:
			pass
		else:
			self.loadPlaneModel(model_to_load)

		if not specs_to_load:
			if not model_to_load:
				self.loadSpecs(name)
			else:
				self.loadSpecs(model_to_load)
		elif specs_to_load == 0:
			pass
		else:
			self.loadSpecs(specs_to_load)

		#self.name = name
		#self.roll_speed = 50
		#self.pitch_speed = 50
		#self.yaw_speed = 50

	def loadPlaneModel(self, model, force=False):
		'''loads model for a plane. force if there's already one loaded'''

		# i heard that hasattr isn't that good. should i set the var to
		# None in __init__ instead?
		if hasattr(self, "plane_model"):
			if force:
				self.plane_model = loader.loadModel(model)
				self.plane_model.reparentTo(self.dummy_node)
			else:
				print 'craft already has a model. force to change'
				return 1
		else:
			self.plane_model = loader.loadModel(model)
			self.plane_model.reparentTo(self.dummy_node)
	
	def loadSpecs(self, s, force=False):
		def justLoad():
			self.mass = specs.getint(s, 'mass')
			self.max_speed = specs.getint(s, 'max_speed')
			self.roll_speed = specs.getint(s, 'roll_speed')
			self.pitch_speed = specs.getint(s, 'pitch_speed')
			self.yaw_speed = specs.getint(s, 'yaw_speed')

		if hasattr(self, "specs_loaded"):
			if force:
				justLoad()
			else:
				print 'craft already has specs assigned. force to change'
				return 1
			self.specs_loaded = True
		else:
			justLoad()

	def move(self, movement):

		# todo: physical correct slackness


		if movement == "roll-left":
			self.dummy_node.setR(self.plane_model, -1 * self.roll_speed * c.getDt())
			print 1 - abs(90 - abs(self.dummy_node.getHpr()[2])) / 90
		if movement == "roll-right":
			self.dummy_node.setR(self.plane_model, self.roll_speed * c.getDt())
			print 1 - abs(90 - abs(self.dummy_node.getHpr()[2])) / 90
		if movement == "pitch-up":
			self.dummy_node.setP(self.plane_model, self.pitch_speed * c.getDt())
		if movement == "pitch-down":
			self.dummy_node.setP(self.plane_model, -1 * self.pitch_speed * c.getDt())
		if movement == "heap-left":
			self.dummy_node.setH(self.plane_model, -1 * self.yaw_speed * c.getDt())
		if movement == "heap-right":
			self.dummy_node.setH(self.plane_model, self.yaw_speed * c.getDt())
		if movement == "move-forward":
			sign = [1,1,1]
			if self.dummy_node.getHpr()[0] > 0:
				sign[0] = -1
			if self.dummy_node.getHpr()[0] < -90 or self.dummy_node.getHpr()[0] > 90:
				sign[1] = -1
			if self.dummy_node.getHpr()[1] < 0:
				sign[2] = -1
			self.dummy_node.setFluidPos(self.dummy_node.getPos()[0] + self.max_speed * c.getDt() * sign[0] * (1 - abs(90 - abs(self.dummy_node.getHpr()[0])) / 90), self.dummy_node.getPos()[1] + self.max_speed * c.getDt() * sign[1] * abs(90 - abs(self.dummy_node.getHpr()[0])) / 90, self.dummy_node.getPos()[2] + self.max_speed * c.getDt() * sign[2] * (1 - abs(90 - abs(self.dummy_node.getHpr()[1])) / 90))
			if self.dummy_node.getHpr()[2] < 0:
				self.dummy_node.setHpr(self.dummy_node.getHpr()[0] + 40 * c.getDt() * (1 - abs(90 - abs(self.dummy_node.getHpr()[2])) / 90), self.dummy_node.getHpr()[1], self.dummy_node.getHpr()[2])
			elif self.dummy_node.getHpr()[2] > 0:
				self.dummy_node.setHpr(self.dummy_node.getHpr()[0] - 40 * c.getDt() * (1 - abs(90 - abs(self.dummy_node.getHpr()[2])) / 90), self.dummy_node.getHpr()[1], self.dummy_node.getHpr()[2])
