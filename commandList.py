commands={}

async def isCommand(message):
	for cmd in commands.keys():
		if message.content.startswith(cmd):
			return 1
	return 0
