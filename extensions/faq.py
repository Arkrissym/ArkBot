#MIT License

#Copyright (c) 2017-2018 Arkrissym

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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
