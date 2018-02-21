from discord.ext import commands

class faq:
	def __init__(self, bot):
		self.bot=bot
		self.faqs=[]

		file=open('faq.txt', 'r')
		line=file.readline()
		while line != '':
			line=line[:-1]
			self.faqs.append(line)
			file.readline()
			line=file.readline()
		file.close()

	async def on_message(self, message):
		for q in self.faqs:
			if message.content == q:
				file=open('faq.txt', 'r')
				line=file.readline()
				while line != '':
					if line[:-1] == message.content:
						await message.channel.send(file.readline())
					line=file.readline()
				file.close()
				return

def setup(bot):
	bot.add_cog(faq(bot))
