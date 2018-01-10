from commandList import *

async def clearLog(client, message):
	if message.author.server_permissions.manage_messages == False:
		print(message.author.name + " doesn't have permission to manage messages.")
		msg="Sorry " + message.author.nick + ". Du hast zu wenig Rechte, um diesen Befehl zu nutzen."
		await client.send_message(message.channel, msg)
		return

	async for log in client.logs_from(message.channel, limit=1000):
		if log.author == client.user:
			await client.delete_message(log)
		elif await isCommand(log):
			await client.delete_message(log)

commands.update({'!clearlog' : clearLog})
