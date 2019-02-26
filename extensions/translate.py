#MIT License

#Copyright (c) 2017-2019 Arkrissym

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

import googletrans
import discord
from discord.ext import commands
import re
import unicodedata
import pycountry
from babel import Locale

class Translator(commands.Cog):
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if isinstance(reaction.emoji, discord.Emoji):
			name=reaction.emoji.name
		else:
			name=reaction.emoji

		#convert to country code
		L1=int(ord(name[0])) + 0x41 - 0x1F1E6
		L2=int(ord(name[1])) + 0x41 - 0x1F1E6

		try:
			name=str(chr(L1) + chr(L2))
		except:
			return

		#check if it is a country code
		try:
			pycountry.countries.get(alpha_2=name)
		except:
			return

		#get language
		locale=str(Locale.parse('und_{}'.format(name)))
		locale=locale[:2]

		#translate
		translation=googletrans.Translator().translate(reaction.message.content, dest=locale).text
		try:
			await reaction.message.channel.send(translation)
		except:
			pass

def setup(bot):
	bot.add_cog(Translator())
