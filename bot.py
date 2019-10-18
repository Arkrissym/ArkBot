#MIT License

#Copyright (c) 2017-2019 Arkrissym

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

import discord
from discord.ext import commands

import asyncio
import random
import os
import itertools
import inspect

from logger import logger
import config
import dataBase

async def get_prefix(bot, message):
	r=list()
	if message.guild != None:
		r.extend([config.getPrefix(message.guild.id)])
	else:
		r.extend([config.config['bot']['cmd_prefix']])
	r.extend(commands.when_mentioned(bot, message))

	return r

class MyHelpCommand(commands.DefaultHelpCommand):
	def command_not_found(self, string):
		locale=config.getLocale(self.context.guild.id)
		return config.strings[locale]["bot"]["command_not_found"].format(string)

	def subcommand_not_found(self, command, string):
		locale=config.getLocale(self.context.guild.id)
		if isinstance(command, commands.Group) and len(command.all_commands) > 0:
			return config.strings[locale]["bot"]["sub_command_not_found_1"].format(command, string)
		return config.strings[locale]["bot"]["sub_command_not_found_2"].format(command)

	def get_ending_note(self):
		locale=config.getLocale(self.context.guild.id)
		command_name = self.context.invoked_with
		return config.strings[locale]["bot"]["help_command_ending_note"].format(self.clean_prefix, command_name)

	def add_indented_commands(self, commands, *, heading, max_size=None):
		if not commands:
			return

		locale=config.getLocale(self.context.guild.id)

		self.paginator.add_line(heading)
		max_size = max_size or self.get_max_size(commands)

		get_width = discord.utils._string_width
		for command in commands:
			name = command.name
			width = max_size - (get_width(name) - len(name))

			short_doc=command.short_doc
			try:
				module_name=short_doc.split("+")[0]
				string_name=short_doc.split("+")[1]
				short_doc=config.strings[locale][module_name][string_name]
			except:
				pass

			entry = '{0}{1:<{width}} {2}'.format(self.indent * ' ', name, short_doc, width=width)
			self.paginator.add_line(self.shorten_text(entry))

	def add_command_formatting(self, command):
		locale=config.getLocale(self.context.guild.id)

		if command.description:
			description=command.description
			try:
				module_name=short_doc.split("+")[0]
				string_name=short_doc.split("+")[1]
				description=config.strings[locale][module_name][string_name]
			except:
				pass
			self.paginator.add_line(description, empty=True)

		signature = self.get_command_signature(command)
		self.paginator.add_line(signature, empty=True)

		if command.help:
			help=command.help
			try:
				module_name=short_doc.split("+")[0]
				string_name=short_doc.split("+")[1]
				help=config.strings[locale][module_name][string_name]
			except:
				pass
			self.paginator.add_line(help, empty=True)


bot=commands.AutoShardedBot(command_prefix=get_prefix, help_command=MyHelpCommand())

@bot.event
async def on_ready():
	try:
		with open("build_date.txt") as build_date:
			logger.info("Docker image built at: {}".format(build_date.readline()))
			build_date.close()
	except:
		pass

	logger.info('Logged in as ' + bot.user.name)
	logger.info('discord.py version: ' + discord.__version__)
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='github.com/Arkrissym/ArkBot'), afk=False)

	#fetch config from database
	for g in bot.guilds:
		config.getLocale(g.id)

@bot.event
async def on_disconnect():
	bot.connect()

@bot.event
async def on_member_join(member):
	Msg=config.strings[config.getLocale(member.guild.id)]['bot']['member_join_msg']
	msg=random.randint(0, len(Msg) - 1)
	ch=member.guild.system_channel
	if not ch:
		for ch in member.guild.text_channels:
			break

	await ch.send(Msg[msg].format(member.name))

@bot.event
async def on_member_remove(member):
	Msg=config.strings[config.getLocale(member.guild.id)]['bot']['member_remove_msg']
	msg=random.randint(0, len(Msg) - 1)
	ch=member.guild.system_channel
	if not ch:
		for ch in member.guild.text_channels:
			break

	await ch.send(Msg[msg].format(member.name))

@bot.event
async def on_member_ban(guild, user):
	ch=guild.system_channel
	if not ch:
		for ch in guild.text_channels:
			break

	await ch.send(config.strings[config.getLocale(guild.id)]['bot']['member_ban_msg'].format(user.name))

@bot.event
async def on_member_unban(guild, user):
	ch=guild.system_channel
	if not ch:
		for ch in guild.text_channels:
			break

	await ch.send(config.strings[config.getLocale(guild.id)]['bot']['member_unban_msg'].format(user.name))


for ext in config.config['bot']['extensions'].split():
	try:
		bot.load_extension(ext)
	except Exception as e:
		logger.error('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

#read the token from token.txt
try:
	tokenFile=open("token.txt", "r")
	token=tokenFile.readline()
	tokenFile.close()
	#remove \n at the end of the line
	token=token[:-1]
except:
	token=os.getenv("DISCORD_TOKEN")

if token == None:
	logger.fatal("No token for discord found. Please save a token.txt or specify a environment variable 'DISCORD_TOKEN'.")
else:
	bot.run(token)
