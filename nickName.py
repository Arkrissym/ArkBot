from commandList import *
import asyncio
import random
from faker import Faker

nameList=[
	'Noname',
	'Alphakevin',
	'Chantal',
	'Teemo',
	'Peter Müller, Klasse 2C',
	'Count Schoko',
	'Bob Ross',
	'Donald Trump',
	'Angela Merkel',
	'Barack Obama',
	'Zeuge Seehofas',
	'Karsten Stahl',
	'Hans Jörg'
]

fake=Faker('de_DE')

async def setYourMom(client, message):
	oldName=message.author.nick
	await client.change_nickname(message.author, 'Deine Mudda')
	await asyncio.sleep(20)
	await client.change_nickname(message.author, oldName)
	await client.delete_message(message)

async def setRandomNick(client, message):
	if random.randint(0, 2) < 1:
		await client.change_nickname(message.author, nameList[random.randint(0, len(nameList) - 1)])
	else:
		await client.change_nickname(message.author, fake.name())

commands.update({'!yourmom' : setYourMom})
commands.update({'!randomnick' : setRandomNick})
commands.update({'!setnick' : setRandomNick})
