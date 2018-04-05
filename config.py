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
import discord
from discord.ext import commands
from logger import logger as log

config={}
strings={}
_initialized=False

def load_locales(locale):
	try:
		for file in os.listdir('{}/locales/{}'.format(os.path.dirname(__file__), locale)):
			if os.path.isfile('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file)) and file.endswith('.json'):
				try:
					with open('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file), 'r', encoding='utf-8') as str_file:
						data=json.load(str_file)
						for key in data.keys():
							strings[file[:-5]][key]=data[key]
				except Exception as e:
					log.warning('{}: failed to open {}: {}'.format(locale, file, str(e)))
	except Exception as e:
		log.error('failed to load translation: {}'.format(str(e)))


if _initialized == False:
	try:
		config=ConfigParser(interpolation=ExtendedInterpolation())
		config.read('config.cfg')
	except Exception as e:
		log.error('failed to load config: ' + str(e))

	locale='default'

	try:
		for file in os.listdir('{}/locales/{}'.format(os.path.dirname(__file__), locale)):
			if os.path.isfile('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file)) and file.endswith('.json'):
				try:
					with open('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file), 'r', encoding='utf-8') as str_file:
						strings[file[:-5]]=json.load(str_file)
				except Exception as e:
					log.warning('{}: failed to open {}: {}'.format(locale, file, str(e)))
	except Exception as e:
		log.error('failed to load default strings: {}'.format(str(e)))

	if 'bot' in config:
		if 'locale' in config['bot']:
			locale=config['bot']['locale']
			if locale != 'default':
				load_locales(locale)

	_initialized=True

class Config:
	def __init__(self, bot):
		self.bot=bot

	@commands.command(pass_context=True)
	@commands.is_owner()
	async def list_locales(self, ctx):
		text=str()
		for locale in os.listdir('{}/locales/'.format(os.path.dirname(__file__))):
			text='{}\n{}'.format(text, locale)

		embed=discord.Embed(title=strings['config']['list_of_locales'], description=text)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True)
	@commands.is_owner()
	async def set_locale(self, ctx, *, locale : str):
		locale_avail=False

		for l in os.listdir('{}/locales/'.format(os.path.dirname(__file__))):
			if locale == l:
				locale_avail=True

		if locale_avail:
			load_locales(locale)
			if 'bot' in config:
				config['bot']['locale']=locale

			await ctx.send(strings['config']['set_locale'].format(locale))
		else:
			await ctx.send(strings['config']['locale_not_found'].format(locale))

def setup(bot):
	bot.add_cog(Config(bot))