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
import psycopg2
import psycopg2.extras
from psycopg2 import sql

config={}
strings={}
_initialized=False

guild_config={}

def load_locales():
	try:
		for locale in os.listdir('{}/locales/'.format(os.path.dirname(__file__))):
			strings.update({locale : {}})
			#load default strings first
			try:
				for file in os.listdir('{}/locales/{}'.format(os.path.dirname(__file__), "default")):
					if os.path.isfile('{}/locales/{}/{}'.format(os.path.dirname(__file__), "default", file)) and file.endswith('.json'):
						try:
							str_file = open('{}/locales/{}/{}'.format(os.path.dirname(__file__), "default", file), 'r', encoding='utf-8')
							strings[locale][file[:-5]]=json.load(str_file)
							str_file.close()
						except Exception as e:
							log.warning('{}: failed to open {}: {}'.format("Default", file, str(e)))
			except Exception as e:
				log.error('failed to load default strings: {}'.format(str(e)))

			#load translation
			for file in os.listdir('{}/locales/{}'.format(os.path.dirname(__file__), locale)):
				if os.path.isfile('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file)) and file.endswith('.json'):
					try:
						str_file = open('{}/locales/{}/{}'.format(os.path.dirname(__file__), locale, file), 'r', encoding='utf-8')
						data=json.load(str_file)
						for key in data.keys():
							strings[locale][file[:-5]][key]=data[key]
						str_file.close()
					except Exception as e:
						log.warning('{}: failed to open {}: {}'.format(locale, file, str(e)))
	except Exception as e:
		log.error('failed to load strings: {}'.format(str(e)))


if _initialized == False:
	try:
		config=ConfigParser(interpolation=ExtendedInterpolation())
		config.read('config.cfg')
	except Exception as e:
		log.error('failed to load config: ' + str(e))

	load_locales()

	_initialized=True


def sqlReadConfig(id):
	if str(id) in guild_config.keys():
		return [id, guild_config[str(id)]["prefix"], guild_config[str(id)]["locale"]]

	conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
	cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
	cur.execute(sql.SQL("SELECT * FROM config WHERE id = %s"), [str(id)])

	ret = None
	for row in cur:
		if row[0] == str(id):
			ret = row
			guild_config[str(id)]={
				"prefix" : ret[1],
				"locale" : ret[2]
				}

	cur.close()
	conn.close()

	return ret

def sqlSaveConfig(id, prefix, locale):
	try:
		conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
		cur=conn.cursor()

		old = sqlReadConfig(id)
		if old == None:
			cur.execute(sql.SQL("INSERT INTO config VALUES (%s, %s, %s)"), [str(id), prefix, locale])
		else:
			cur.execute(sql.SQL("UPDATE config SET id = %s, prefix = %s, locale = %s WHERE id = %s"), [str(id), prefix, locale, str(id)])	
	
		conn.commit()

		cur.close()
		conn.close()
	except:
		pass

	guild_config[str(id)]={
		"prefix" : prefix,
		"locale" : locale
		}

	return 1

def getPrefix(guild_id):
	try:
		data=sqlReadConfig(guild_id)
	except:
		return config['bot']['cmd_prefix']

	if data == None:
			return config['bot']['cmd_prefix']

	return data[1]

def getLocale(guild_id):
	try:
		data=sqlReadConfig(guild_id)
	except:
		return config['bot']['locale']

	if data == None:
		return config['bot']['locale']

	return data[2]


def is_admin_or_owner():
	async def predicate(ctx):
		permissions=ctx.channel.permissions_for(ctx.author)
		return await ctx.bot.is_owner(ctx.author) or permissions.administrator

	return commands.check(predicate)

class Config:
	def __init__(self, bot):
		self.bot=bot

	@commands.command(pass_context=True, no_pm=True)
	@is_admin_or_owner()
	async def list_locales(self, ctx):
		text=str()
		for locale in os.listdir('{}/locales/'.format(os.path.dirname(__file__))):
			text='{}\n{}'.format(text, locale)

		embed=discord.Embed(title=strings[getLocale(ctx.guild.id)]['config']['list_of_locales'], description=text)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	@is_admin_or_owner()
	async def set_locale(self, ctx, *, locale : str):
		locale_avail=False

		for l in os.listdir('{}/locales/'.format(os.path.dirname(__file__))):
			if locale == l:
				locale_avail=True

		if locale_avail:
			sqlSaveConfig(ctx.guild.id, getPrefix(ctx.guild.id), locale)

			await ctx.send(strings[getLocale(ctx.guild.id)]['config']['set_locale'].format(locale))
		else:
			await ctx.send(strings[getLocale(ctx.guild.id)]['config']['locale_not_found'].format(locale))

	@commands.command(pass_context=True, no_pm=True)
	@is_admin_or_owner()
	async def set_prefix(self, ctx, prefix : str):
		if len(prefix) == 0 or len(prefix) > 5 or prefix.startswith("@") or prefix.startswith("#"):
			await ctx.send(strings[getLocale(ctx.guild.id)]['config']['invalid_prefix'])
		else:
			sqlSaveConfig(ctx.guild.id, prefix, getLocale(ctx.guild.id))
			await ctx.send(strings[getLocale(ctx.guild.id)]['config']['set_prefix'].format(prefix))

def setup(bot):
	bot.add_cog(Config(bot))
