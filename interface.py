def printInstructions(instructions = ""):
	'''give me some text and i'll print it at top left corner'''
	from direct.gui.DirectGui import OnscreenText
	from pandac.PandaModules import TextNode
	OnscreenText(
		text = instructions,
		style = 1,
		fg = (1,1,1,1),
		pos = (-1.3, 0.95),
		align = TextNode.ALeft,
		scale = .05)
