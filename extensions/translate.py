import googletrans
import discord
import re
import unicodedata
import pycountry
from babel import Locale

class Translator:
	def __init__(self, bot):
		self.bot=bot

	async def on_reaction_add(self, reaction, user):
		if isinstance(reaction.emoji, discord.Emoji):
			print("discord.Emoji")
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
		#print(locale)

		#translate
		translation=googletrans.Translator().translate(reaction.message.content, dest=locale).text
		try:
			await reaction.message.channel.send(translation)
		except:
			pass

def setup(bot):
	bot.add_cog(Translator(bot))