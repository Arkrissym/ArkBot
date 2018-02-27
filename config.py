import json
from configparser import ConfigParser, ExtendedInterpolation
import os

config={}
strings={}
_initialized=False

if _initialized == False:
	try:
		config=ConfigParser(interpolation=ExtendedInterpolation())
		config.read('config.cfg')
#		with open('config.json', 'r') as cfg_file:
#			config=json.load(cfg_file)
#		print(config.sections())
	except Exception as e:
		print('failed to load config: ' + str(e))

	if 'locale' in config['bot']:
		locale=config['bot']['locale']
	else:
		locale='default'

	try:
		for file in os.listdir('locales/{}'.format(locale)):
			if os.path.isfile('locales/{}/{}'.format(locale, file)) and file.endswith('.json'):
				try:
					with open('locales/{}/{}'.format(locale, file), 'r') as str_file:
						strings[file[:-5]]=json.load(str_file)
				except:
					print('failed to open {}'.format(file))
	except:
		print('failed to load strings')

#	print(strings)
	_initialized=True
