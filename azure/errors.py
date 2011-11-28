"""Error handling."""

import sys

# Constants used for the err_action variable
IGNORE_ALL, IGNORE, RAISE, DIE = range(4)

# IGNORE_ALL - Ignore an AzureError, and don't print AzureError messages
# IGNORE - Ignore an AzureError, but print AzureError messages
# RAISE - Keep the thrown AzureError raised for some other code to handle
# DIE - Die on a thrown AzureError; 
err_action = RAISE

def setErrAction(actionNum):
    """Sets error handling option"""
    global err_action
    err_action = actionNum

def handleError(error):
    """Handles an AzureError exception based on some configuration settings."""
    # NOTE: This subroutine should only be used for handling non-critical errors
    # (i.e. when the game can still more or less function).  Other, more serious
    # errors, should be handled manually

    if err_action == IGNORE_ALL:
        pass
    elif err_action == IGNORE:
        sys.stderr.write(error.message)
    elif err_action == RAISE:
        raise error
    elif err_action == DIE:
        sys.stderr.write(error.message)
        sys.exit(1)
    else:
        raise ParamError("Error when raising error! Invalid value for"\
                         "handleError(): {}".format(err_action))


class AzureError(Exception):
    pass


class ResourceLoadError(AzureError):
    """Should be thrown when a resource is improperly loaded or fails to load
    at all."""
    def __init__(self, resource="None", details="None"):
        self.message = "Failed to load resource: {}\n"\
                       "\tDetails: {}".format(resource, details)
        self.resource = resource
    def __str__(self):
        return self.message


class ResourceHandleError(AzureError):
    """Should be thrown when an attempt is made to use a resource in a way
    that was not intended."""
    def __init__(self, resource="None", details="None"):
        self.message = "Error handling resource: {}\n "\
                       "\tDetails: {}".format(resource, details)
        self.resource = resource
    def __str__(self):
        return self.message


class ParamError(AzureError):
    """Should be thrown when an invalid value is given to a function."""
    def __init__(self, message=None):
        self.message = message
    def __str__(self):
        return self.message


class BaseMissing(AzureError):
    """ShowBase builtins are needed but not available."""
    def __init__(self, message="Missing base or some of its builtins. "\
                               "Are you sure ShowBase is initialized?"):
        self.message = message
    def __str__(self):
        return self.message


class ScenarioLoadingError(AzureError):
    """A scenario was requested that is not available."""
    def __init__(self, scenario):
        self.message = "The requested scenario '{}' could not "\
                       "be found.".format(scenario)
    def __str__(self):
        return self.message
