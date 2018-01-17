import discord
import asyncio
import logging
import logging.handlers

from commandList import *
import dataBase

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
	for name in commands.keys():
		if name.startswith('!'):
			string=string + name + '\n'
		else:
			easterEggs+=1
	string=string + '\nEs gibt ' + str(easterEggs) + ' versteckte Befehle.'
	await client.send_message(message.channel, string)

commands.update({'!commands' : listCommands})

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

	for cmd in commands.keys():
		if message.content == cmd:
			logger.info(message.author.name + ' called: ' + cmd)
			await commands[cmd](client, message)
			n=dataBase.readVal(message.author.name, message.channel, cmd)
#			if n:
			dataBase.writeVal(message.author.name, message.channel, cmd, n+1)
#			else:
#				dataBase.writeVal(message.author.name, cmd, 1)
			return

	for cmd in commands.keys():
		if message.content.startswith(cmd + ' '):
			logger.info(message.author.name + ' called ' + cmd)
			await commands[cmd](client, message)
			n=dataBase.readVal(message.author.name, message.channel, cmd)
#			if n:
			dataBase.writeVal(message.author.name, message.channel, cmd, n+1)
#			else:
#				dataBase.writeVal(message.author.name, cmd, 1)
			return

#read the token from token.txt
tokenFile=open("token.txt", "r")
token=tokenFile.readline()
tokenFile.close()

#remove \n at the end of the line
token=token[:-1]

client.run(token)
