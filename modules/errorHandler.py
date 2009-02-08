import sys

# Constants used for the errAction variable
DIE, RAISE, IGNORE, IGNORE_SILENT = range(4)

# DIE - Die on a thrown AzureError; 
# RAISE - Keep the thrown AzureError raised for some other code to handle
# IGNORE - Ignore an AzureError, but print AzureError messages
# IGNORE_SILENT - Ignore an AzureError, and don't print AzureError messages
errAction = RAISE

def setErrAction(actionNum):
	global errAction
	errAction = actionNum

def handleError(error):
	""" Handles an AzureError exception based on some configuration settings """
	# NOTE: This subroutine should only be used for handling non-critical errors
	# (i.e. when the game can still more or less function).  Other, more serious
	# errors, should be handled manually
	
	if errAction == DIE:
		sys.stderr.write(error.message)
		sys.exit(1)
	elif errAction == IGNORE:
		sys.stderr.write(error.message)
	elif errAction == RAISE:
		raise error
	elif errAction == IGNORE_SILENT:
		pass
	else:
		raise ParamError("Error when raising error!  Invalid value for handleError(): %d" % errAction)

class AzureError(Exception):
	pass

class ResourceLoadError(AzureError):
	""" Should be thrown when a resource is improperly loaded or fails to load at all """
	
	def __init__(self, resource="None", details="None"):
		self.message = "Failed to load resource: %s\n\tDetails: %s" % (resource, details)
		self.resource = resource
		
	def __str__(self):
		return self.message
		
class ResourceHandleError(AzureError):
	""" Should be thrown when an attempt is made to use a resource in a way that was not intended """
	
	def __init__(self, resource="None", details="None"):
		self.message = "Error handling resource: %s\n\tDetails: %s" % (resource, details)
		self.resource = resource
		
	def __str__(self):
		return self.message
		
class ParamError(AzureError):
	""" Should be thrown when an invalid value is given to a function """
	
	def __init__(self, message=None):
		self.message = message
		
	def __str__(self):
		return self.message


		
		