import discord
import asyncio
import logging
import logging.handlers

from commandList import *

import testModule
import uptime
import zeit
import faq
import clearHistory
import nickName

client=discord.Client()

async def listCommands(client, message):
	easterEggs=0
	string='Liste (fast) aller Befehle:\n'
	for name in commandNames:
		if name.startswith('!'):
			string=string + name + '\n'
		else:
			easterEggs+=1
	string=string + '\nEs gibt ' + str(easterEggs) + ' versteckte Befehle.'
	await client.send_message(message.channel, string)

commands.update({'!commands' : listCommands})
commandNames.append('!commands')

logger=logging.getLogger('ArkBot')
logger.setLevel(logging.DEBUG)

#fh=logging.FileHandler('ArkBot.log')
fh=logging.handlers.RotatingFileHandler('/var/log/ArkBot.log', maxBytes=1024*1024, backupCount=3)
fh.setLevel(logging.INFO)

ch=logging.StreamHandler()
ch.setLevel(logging.ERROR)

fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logger.addHandler(fh)
logger.addHandler(ch)

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
#	print(client.user.id)
	print('------')
	logger.debug('Logged in as ' + client.user.name)

@client.event
async def on_message(message):
#	check, if message has been sent by this bot
	if message.author == client.user:
		return

	for cmd in commandNames:
		if message.content.startswith(cmd):
			logger.info(message.author.name + ' called ' + cmd)
			await commands[cmd](client, message)

#read the token from token.txt
tokenFile=open("token.txt", "r")
token=tokenFile.readline()
tokenFile.close()

#remove \n at the end of the line
token=token[:-1]

client.run(token)
