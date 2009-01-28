'''get key events and do stuff. controls are independent of set keys'''

import sys
from direct.showbase.DirectObject import DirectObject

class keyHandler(DirectObject):
	'''get key events and do stuff. controls are independent of set keys'''

	def __init__(self):
		'''setup control keys and event handlers'''
		
		# non-continous
		self.accept("escape", sys.exit)

		# continous
		self.controls = {
			"a": "roll-left",
			"d": "roll-right",
			"s": "pitch-up",
			"w": "pitch-down",
			"q": "heap-right",
			"e": "heap-left",
			"space": "move-forward"
			}

		# at start no key is active
		self.keyStates = {}
		for i in self.controls:
			action = self.controls[i]
			self.keyStates[action] = 0

		# go through keys and 'accept' them
		for key, action in self.controls.items():
			self.accept(key, self.chKeyState, [action, 1])
			self.accept(key+"-up", self.chKeyState, [action, 0])

	def chKeyState(self, action, value):
		self.keyStates[action] = value
