'''get key events and do stuff. controls are independent of set keys'''

import sys
import camBackend
from direct.showbase.DirectObject import DirectObject

class keyHandler(DirectObject):
	'''get key events and do stuff. controls are independent of set keys'''

	def __init__(self, ctlMap):
		'''setup control keys and event handlers'''
		
		self.ctlMap = ctlMap
		
		# non-continous
		self.accept("escape", sys.exit)

		# at start no key is active
		self.keyStates = {}
		for key in self.ctlMap.controls:
			self.keyStates[key] = 0
			# go through keys and 'accept' them
			self.accept(key, self.chKeyState, [key, 1])
			self.accept(key+"-up", self.chKeyState, [key, 0])

	def chKeyState(self, key, value):
		#print("key %s changed to %d" % (key, value))
		self.keyStates[key] = value
		
class controlMap():
	def __init__(self):
		self.controls = {
			"a": {"type":"move", "desc": "roll-left"},
			"d": {"type":"move", "desc": "roll-right"},
			"s": {"type":"move", "desc": "pitch-up"},
			"w": {"type":"move", "desc": "pitch-down"},
			"q": {"type":"move", "desc": "heap-right"},
			"e": {"type":"move", "desc": "heap-left"},
			"space": {"type":"move", "desc": "move-forward"},
			"shift": {"type":"move", "desc": "brakes"},
			"z": {"type":"cam-move", "desc": "move-left"},
			"c": {"type":"cam-move", "desc": "move-right"},
			"x": {"type":"cam-move", "desc": "move-origin"},
			"p": {"type":"cam-view", "desc": camBackend.FIRST_PERSON},
			"o": {"type":"cam-view", "desc": camBackend.COCKPIT},
			"i": {"type":"cam-view", "desc": camBackend.THIRD_PERSON},
			"u": {"type":"cam-view", "desc": camBackend.DETACHED}
			}
