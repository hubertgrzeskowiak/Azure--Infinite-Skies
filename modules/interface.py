"""Module containing graphical user interface objects"""

def printInstructions(instructions = ""):
	"""Give me some text and i'll print it at the top left corner"""
    # temporary function. used until we have some real interface
	from direct.gui.DirectGui import OnscreenText
	from pandac.PandaModules import TextNode
	OnscreenText(
		text = instructions,
		style = 1,
		fg = (1,1,1,1),
		pos = (-1.3, 0.95),
		align = TextNode.ALeft,
		scale = .05)
