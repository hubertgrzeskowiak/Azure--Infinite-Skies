'''this module manages everthing around loading, setting and moving aircrafts'''

from pandac.PandaModules import ClockObject
c = ClockObject.getGlobalClock()

import ConfigParser
specs = ConfigParser.SafeConfigParser()
specs.read('etc/CraftSpecs.cfg')
from math import cos, sin, radians
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
		self.thrust= 0 #added these for the physics 
		self.counter=0 
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

		# I haven't changed this part too much to keep it as it was so people could work on it using the ghost mode, I am posting this so we could start working on 
		# the physics of the game, I tried different ways and this gave the best result, there are many more ways to do this maybe better ways, so feel free to 
		# change anywhere you like, don't forgeet the comment the line calling the velocity function at the main.py

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
		if movement == 'move-forward':#if you want to want to work with physics make this a comment line
			# 40pu/s = ~12,4km/h
			self.dummy_node.setFluidY(self.dummy_node, 40 * dt)#make this line also a comment
		#this is the part I added, so just erase the """.
		"""if movement == 'move-forward' and self.thrust<100: 									
			self.thrust +=1 #increases the thrust
		if movement == 'brakes'and self.thrust>0:
			self.thrust -=1 #decreases
	def velocity(self):
		self.k=0.01 #coefficient for the lift force, I found it by experimentation but it will be better to have an analytical solution
		dt = c.getDt()
		self.pitch_ang=radians(self.dummy_node.getP())#radian value of the planes orientation
		self.roll_ang=radians(self.dummy_node.getR())
		self.heap_ang=radians(self.dummy_node.getH())
		self.gravity=-9.81*500 #acceleration of gravity but it was so small value so I multiplied it with 500 also found by experimenting but will change after the 						#analytical solution
		self.ForceZ=(self.thrust*cos(self.heap_ang)+self.k*self.thrust*cos(self.roll_ang))*80000 #this force is to the z axis of the plane(not the relative axis), so 														#it does not have gravity but the thrust and the lift force, 80000 is 													#also an experimental value will change after the solution 
		self.dummy_node.setFluidY(self.dummy_node, self.thrust*dt) #this makes the plane go forward through its own axis
		self.dummy_node.setZ(self.dummy_node.getZ()+self.gravity*dt*dt/2)# this adds the gravity, it moves the plane at the direction of the z axis of the ground
		self.dummy_node.setFluidZ(self.dummy_node, self.ForceZ*dt*dt/2/self.mass)#this adds the movement at the z direction of the plane
		if self.dummy_node.getZ()<0: self.dummy_node.setZ(0)#this makes the plane not to go below"""

	def getBounds(self):
		'''returns a vector describing the vehicle's size (width, length,
		height). useful for collision detection'''
		bounds = self.dummy_node.getTightBounds()
		size = bounds[1] - bounds[0]
		return size
