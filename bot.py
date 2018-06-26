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

class myHelpFormatter(discord.ext.commands.HelpFormatter):
	def _add_subcommands_to_page(self, max_width, commands):
		locale=config.getLocale(self.context.guild.id)

		for name, command in commands:
			if name in command.aliases:
				# skip aliases
				continue

			short_doc=command.short_doc

			try:
				module_name=short_doc.split("+")[0]
				string_name=short_doc.split("+")[1]
				#if module_name in config.strings[locale].keys() and string_name in config.strings[locale][module_name].keys():
				short_doc=config.strings[locale][module_name][string_name]
			except:
				pass

			#print(short_doc)

			entry = '  {0:<{width}} {1}'.format(name, short_doc, width=max_width)
			shortened = self.shorten(entry)
			self._paginator.add_line(shortened)

	async def format(self):
		#print("format")

		locale=config.getLocale(self.context.guild.id)

		self._paginator = discord.ext.commands.Paginator()

		# we need a padding of ~80 or so

		description = self.command.description if not self.is_cog() else inspect.getdoc(self.command)

		if description:
			try:
				module_name=description.split("+")[0]
				string_name=description.split("+")[1]
				#if module_name in config.strings[locale].keys() and string_name in config.strings[locale][module_name].keys():
				description=config.strings[locale][module_name][string_name]
			except:
				pass

			# <description> portion
			self._paginator.add_line(description, empty=True)
			#print(description)

		if isinstance(self.command, discord.ext.commands.Command):
			# <signature portion>
			signature = self.get_command_signature()
			self._paginator.add_line(signature, empty=True)
			#print("signature: " + signature)

			# <long doc> section
			if self.command.help:
				cmd_help=self.command.help

				try:
					module_name=cmd_help.split("+")[0]
					string_name=cmd_help.split("+")[1]
					#if module_name in config.strings[locale].keys() and string_name in config.strings[locale][module_name].keys():
					cmd_help=config.strings[locale][module_name][string_name]
				except:
					pass
				self._paginator.add_line(cmd_help, empty=True)
				#print(cmd_help)

			# end it here if it's just a regular command
			if not self.has_subcommands():
				self._paginator.close_page()
				return self._paginator.pages

		max_width = self.max_name_size

		def category(tup):
			cog = tup[1].cog_name
			# we insert the zero width space there to give it approximate
			# last place sorting position.
			return cog + ':' if cog is not None else '\u200bNo Category:'

		filtered = await self.filter_command_list()
		if self.is_bot():
			data = sorted(filtered, key=category)
			for category, commands in itertools.groupby(data, key=category):
				# there simply is no prettier way of doing this.
				commands = sorted(commands)
				if len(commands) > 0:
					self._paginator.add_line(category)

				#print(category)
				#print(commands)
				self._add_subcommands_to_page(max_width, commands)
		else:
			filtered = sorted(filtered)
			if filtered:
				self._paginator.add_line('Commands:')
				self._add_subcommands_to_page(max_width, filtered)

		# add the ending note
		self._paginator.add_line()
		ending_note = self.get_ending_note()
		self._paginator.add_line(ending_note)
		return self._paginator.pages

async def guild_prefix(bot, message):
	r=list()
	if message.guild != None:
		r.extend([config.getPrefix(message.guild.id)])
	else:
		r.extend([config.config['bot']['cmd_prefix']])
	r.extend(commands.when_mentioned(bot, message))

	return r

bot=commands.AutoShardedBot(command_prefix=guild_prefix, formatter=myHelpFormatter())

@bot.event
async def on_ready():
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
