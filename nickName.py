from commandList import *
import asyncio
import random

nameList=[
	'Noname',
	'Deine Mudda',
	'Alphakevin',
	'Chantal',
	'Winnetouch',
	'Teemo',
	'Jens Maul',
	'Peter Müller, Klasse 2C',
	'Count Schoko',
	'Bob Ross',
	'Donald Trump',
	'Frauke Petry',
	'Angela Merkel',
	'Angelo Merke',
	'Barack Obama',
	'Zeuge Seehofas',
	'Der Reichsbürger',
	'Karsten Stahl',
	'Hans Jörg'
]

async def setYourMom(client, message):
	oldName=message.author.nick
	await client.change_nickname(message.author, 'Deine Mudda')
	await asyncio.sleep(20)
	await client.change_nickname(message.author, oldName)
	await client.delete_message(message)

async def setRandomNick(client, message):
	await client.change_nickname(message.author, nameList[random.randint(0, len(nameList) - 1)])

commands.update({'!yourmom' : setYourMom})
commandNames.append('!yourmom')
commands.update({'!randomnick' : setRandomNick})
commandNames.append('!randomnick')
commands.update({'!setnick' : setRandomNick})
commandNames.append('!setnick')
