from commandList import *
import random

list=[
	'Der Zeiger liegt in der Kurve.',
	'Es ist kurz vor knapp.',
	'Nur noch ein Tag, dann ist morgen.'
]

async def zeit(client, message):
	await client.send_message(message.channel, list[random.randint(0, len(list) - 1)])

commands.update({'!time' : zeit})
commandNames.append('!time')

commands.update({'Wie spät ist es?' : zeit})
commandNames.append('Wie spät ist es?')
