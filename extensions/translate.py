# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import discord
import googletrans
import pycountry
from babel import Locale
from discord.ext import commands


class Translator(commands.Cog):
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		if isinstance(reaction.emoji, discord.Emoji):
			name = reaction.emoji.name
		else:
			name = reaction.emoji

		# convert to country code
		L1 = int(ord(name[0])) + 0x41 - 0x1F1E6
		L2 = int(ord(name[1])) + 0x41 - 0x1F1E6

		try:
			name = str(chr(L1) + chr(L2))
		except:
			return

		# check if it is a country code
		try:
			pycountry.countries.get(alpha_2=name)
		except:
			return

		# get language
		locale = str(Locale.parse('und_{}'.format(name)))
		locale = locale[:2]

		# translate
		translation = googletrans.Translator().translate(reaction.message.content, dest=locale).text
		try:
			await reaction.message.channel.send(translation)
		except:
			pass


def setup(bot):
	bot.add_cog(Translator())
