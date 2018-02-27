#MIT License

#Copyright (c) 2017-2018 Arkrissym

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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

	_initialized=True
