import discord
from discord.ext import commands
import asyncio
import logging
#import logging.handlers
import random

import dataBase

bot=commands.Bot(command_prefix=commands.when_mentioned_or('!'))
client=bot

extensions=[
	'testModule',
	'lolStat.py',
	'faq',
	'nickName',
	'uptime',
	'zeit',
	'clearHistory',
	'music'
]

logger=logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

ch=logging.StreamHandler()
ch.setLevel(logging.INFO)

ch.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))

logger.addHandler(ch)

@bot.event
async def on_ready():
	logger.info('Logged in as ' + client.user.name)
	logger.info('discord.py version: ' + discord.__version__)

@bot.event
async def on_message(message):
#	check, if message has been sent by this bot
	if message.author == bot.user:
		return

	if len(message.content) > 1:
		cmd=bot.get_command(message.content[1:])
		if cmd:
			try:
				logger.info('command ' + cmd.name + ' called.')
				await bot.process_commands(message)

				if hasattr(message.channel, 'server'):
					prefix='messages/' + str(message.channel.server) + '/' + str(message.channel) + '/' + message.author.name
				else:
					prefix='messages/' + message.author.name

				n=dataBase.readVal(prefix, cmd.name)
				dataBase.writeVal(prefix, cmd.name, n+1)
			except Exception as e:
				logger.error('User ' + message.author.name + ' has sent ' + message.content + ' and caused exception: ' + str(e))

@bot.event
async def on_member_join(member):
	Msg=[
		['Willkommen ', '. Denk immer dran: nachts ist es kälter als draußen'],
		['Willkommen ', '. Denk immer dran: Pommes schmecken besser als mit Ketchup.']
	]
	msg=random.randint(0, len(Msg) - 1)
	ch=member.guild.system_channel
	if not ch:
		for ch in member.guild.text_channels:
			break

	await ch.send(Msg[msg][0] + member.name + Msg[msg][1])

@bot.event
async def on_member_remove(member):
	Msg=[
		[' ', ' ist abgedampft. OK Tschüüüüüüsss!'],
		[' ', ' hat n Abgang gemacht.']
	]
	msg=random.randint(0, len(Msg) - 1)
	ch=member.guild.system_channel
	if not ch:
		for ch in member.guild.text_channels:
			break

	await ch.send(Msg[msg][0] + member.name + Msg[msg][1])

@bot.event
async def on_member_ban(guild, user):
	ch=guild.system_channel
	if not ch:
		for ch in guild.text_channels:
			break

	await ch.send(user.name + ' wurde gebannt.')

@bot.event
async def on_member_unban(guild, user):
	ch=guild.system_channel
	if not ch:
		for ch in guild.text_channels:
			break

	await ch.send(user.name + ' wurde entbannt.')


for ext in extensions:
	try:
		bot.load_extension(ext)
	except Exception as e:
		print('Failed to load extension {}\n{}: {}'.format(ext, type(e).__name__, e))

#read the token from token.txt
tokenFile=open("token.txt", "r")
token=tokenFile.readline()
tokenFile.close()

#remove \n at the end of the line
token=token[:-1]

bot.run(token)
