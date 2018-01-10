from commandList import *

async def test(client, message):
	counter=0
	tmp = await client.send_message(message.channel, 'Calculating messages...')
	async for log in client.logs_from(message.channel, limit=1000):
		if log.author == message.author:
			if await isCommand(log) == 0:
				counter+=1

	await client.edit_message(tmp, 'You have {} messages.'.format(counter))

item={'!test' : test}
commands.update(item)
