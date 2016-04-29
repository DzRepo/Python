import ConfigParser
import ErrorHandler
import os

#Settings File Format:
#
#[SectionName]
#parameter=setting
#param2 = setting2
#

def GetSettings(filename, section):
	settings = {}
	config=ConfigParser.RawConfigParser()
	cfg_dir = os.environ['GNIP_CFG']

	try:
		config.read(cfg_dir + "/" + filename)
	except (FileNotFoundError, IOError) as ex:
		ErrorHandler.Log(ex, "Configuration file not found")

	for item in config.items(section):
		settings[item[0]] = item[1]

	return settings
