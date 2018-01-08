commands={}

commandNames=[]

async def isCommand(message):
	for cmd in commandNames:
		if message.content.startswith(cmd):
			return 1
	return 0
