from commandList import *

async def faq(client, message):
	file=open('faq.txt', 'r')
	line=file.readline()
	while line != '':
		if line[:-1] == message.content:
			await client.send_message(message.channel, file.readline())
		line=file.readline()
	file.close()

file=open('faq.txt', 'r')
line=file.readline()
while line != '':
	line=line[:-1]
	commands.update({line : faq})
	file.readline()
	line=file.readline()
file.close()
