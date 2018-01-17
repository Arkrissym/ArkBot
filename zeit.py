from commandList import *
import random

list=[
	'Der Zeiger liegt in der Kurve.',
	'Es ist kurz vor knapp.',
	'Nur noch ein Tag, dann ist morgen.',
	'Zu spät...'
]

async def zeit(client, message):
	await client.send_message(message.channel, list[random.randint(0, len(list) - 1)])

commands.update({'!time' : zeit})
commands.update({'Wie spät ist es?' : zeit})
