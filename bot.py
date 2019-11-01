# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym

import os

import discord
from discord.ext import commands

from core import config
from core.LocalizedHelpCommand import LocalizedHelpCommand
from core.logger import logger


async def get_prefix(bot, message):
	r = list()
	if message.guild is not None:
		r.extend([config.getPrefix(message.guild.id)])
	else:
		r.extend([config.config['bot']['cmd_prefix']])
	r.extend(commands.when_mentioned(bot, message))

	return r


class ArkBot(commands.AutoShardedBot):
	def __init__(self, **options):
		super().__init__(command_prefix=get_prefix, help_command=LocalizedHelpCommand(), **options)

		for ext in config.config['bot']['extensions'].split():
			try:
				logger.info("Loading extension {}".format(ext))
				self.load_extension(ext)
			except Exception as e:
				logger.error('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

	async def on_ready(self):
		try:
			with open("build_date.txt") as build_date:
				logger.info("Docker image built at: {}".format(build_date.readline()))
				build_date.close()
		except:
			pass

		logger.info('Logged in as ' + self.user.name)
		logger.info('discord.py version: ' + discord.__version__)
		await self.change_presence(status=discord.Status.online,
								   activity=discord.Game(name='github.com/Arkrissym/ArkBot'),
								   afk=False)

		# fetch config from database
		for g in self.guilds:
			config.getLocale(g.id)


# read the token from token.txt
try:
	tokenFile = open("token.txt", "r")
	token = tokenFile.readline()
	tokenFile.close()
	# remove \n at the end of the line
	token = token[:-1]
except:
	token = os.getenv("DISCORD_TOKEN")

if token is None:
	logger.fatal(
		"No token for discord found. Please save a token.txt or specify a environment variable 'DISCORD_TOKEN'.")
else:
	ArkBot().run(token)
