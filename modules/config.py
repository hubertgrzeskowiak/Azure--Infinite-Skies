#!/usr/bin/env python
# config.py -- Gives an Interface for configurations

"""
The usage of this module is not as complex as you may think. Look in this
module for the ConfigXXX class, with a format like XML or YAML (for exmaple
ConfigXML) for xml configfile. give the right parameters and after
readAllConfigs(), you can read the configs from the class configxml.config.
For Exmaple:

conf = ConfigXML("/home/user", "azure")
conf.readAllConfigs()
confObj = conf.config

confObj.<option>

Read the description from the Config class too, for how to get options's
values. This is limited.
"""

# Imports
from xml.etree.cElementTree import *
from os.path import join, isdir
from abc import ABCMeta, abstractmethod

#------------------------------------------------------------------------------
# Exception Classes
#------------------------------------------------------------------------------

class AttributeNotExist(Exception): pass
class WrongAttributeType(Exception): pass
class PathNotExist(Exception): pass
class XMLParseError(Exception): pass

#------------------------------------------------------------------------------
# Config Class
#------------------------------------------------------------------------------

class Config(object):
    """The class is teh given object with the needed attributes, it should be
    as most dynamic as it could be.
    
    FIRST OF ALL: YOU WON'T CREATE AN INSTANCE BY YOURESELFE OF THIS CLASS
    you will just get one!
    
    Cause this Object includes all options defined at the beginning and cause
    of its flexible style, it relies under special terms.
    
    1. To read the options you have simply call it as an attribute of the
       object. Exmaple: take the option example above and an object "Config".
       
       Config.optOption : returns the value of the key "optOption"
       
    All attributes not beginning with "opt" stands under the normal python
    class-attribute style. So remember!"""

    def __init__(self):
        pass

#------------------------------------------------------------------------------
    
    def addAttribute(self, attrName, attrValue):
        "Gets the attribute list an add it to the given list"
        
        setattr(self, "opt" + attrName, attrValue)

#------------------------------------------------------------------------------
# Settings Abstract Class
#------------------------------------------------------------------------------

class ConfigAbstract(object):
    
    # Change the Meta class for abstract functionalities
    __metaclass__ = ABCMeta
    
    
    def __init__(self, configPath, configName):
        self.config = Config()  # Create a new config object
        self.attrDict = {}  # Config dict
        self.configPath = configPath  # Just the path to the config file
        self.configName = configName  # Just the name without file ext

    def getConfigObj(self):
        return self.config

    @abstractmethod
    def addConfigAttributes(self, attrDict): pass
    
    @abstractmethod
    def readAllConfigs(self): pass
    
    @abstractmethod
    def writeAllConfigs(self): pass
    
#------------------------------------------------------------------------------
# XML Config Support
#------------------------------------------------------------------------------

class ConfigXML(ConfigAbstract):
    
    def __init__(self, configPath, configName):
        super(ConfigXML, self).__init__(configPath, configName)
        
        self.fullFilename = None
        self.__createFilename()
        
#------------------------------------------------------------------------------

    def __updateConfigObject(self):
        "Updates the config object with the attributes"
        
        for key, value in self.attrDict:
            self.config.addAttribute(key, value)
        
#------------------------------------------------------------------------------

    def __createFilename(self):
        "Just creates the filenname"
    
        # Test for valid dir
        if not isdir(self.configPath):
            raise PathNotExist("The path %s does not exist" % self.configPath)
        
        self.fullFilename = join(self.configPath, self.configName + ".xml")

#------------------------------------------------------------------------------
    
    def __indent(self, elem, level = 0):
        "Makes from xml.etree.cElementTree.Element object looking nice"
    	
        i = "\n" + level * "\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            for e in elem:
                indent(e, level + 1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "\t"
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

#------------------------------------------------------------------------------

    def addConfigAttributes(self, attrDict):
        "Adds all config attributes to the actual dict"
        
        for key, value in attrDict.iteritems():
            if not key.startswith("opt"):
                key = "opt" + key
                
            self.attrDict[key] = value
        
#------------------------------------------------------------------------------

    def readAllConfigs(self):
        "Reads all configurations from the config file"
		
        with open(self.fullFilename, "rb") as cFile:
            xmlFile = parse(cFile)
			
            rootE = xmlFile.getroot()
			
            # Test if the root Element is like we want
            if rootE.tag != "settings":
                raise XMLParseError("Not a valid Xml-Config file.")
			
            name = None
            version = None
            for key, value in rootE.items():
                if key == "version":
                    version = value
                elif key == "name":
                    name = value
			
            if version != "1.0":
                raise XMLParserError("Wrong Xml-Config version")
			    
            # We now search for all options and handle them ...
            for element in rootE.getchildren():
			    
                # Search for the type item
                optType = None
                for key, value in element.items():
                    if key == "type":
                        optType = value
			    
                optName = element.tag
                optValue = element.text.strip()
			    
                try:
                    # Test which type optValue has to be and convert it
                    optTypedValue = None
                    if optType == "string":
                        optTypedValue = str(optValue)
                    elif optType == "integer":
                        optTypedValue = int(optValue)
                    elif optType == "boolean":
                        optTypedValue = bool(optValue)
                    elif optType == "list":
                        optTypedValue = list(optValue)
                    elif optType == "dict":
                        optTypedValue = dict(optValue)
                    else:
                        raise XMLParseError("Not identified type for <%s>" \
                        % optName)
                except Exception as e:
                    print(e)
		        
                # now try to add it, to the config object
                self.attrDict[optName] = optTypedValue
        		    
        self.__updateConfigObject()

#------------------------------------------------------------------------------

    def writeAllConfigs(self):
        "Write all configurations to the file"
        pass
        

