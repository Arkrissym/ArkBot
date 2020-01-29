# MIT License
# see LICENSE for details

# Copyright (c) 2018-2019 Arkrissym


import asyncio
import os
import random

import discord
from discord.ext import commands

from core import config


class MagicShell(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(no_pm=True)
	async def shell(self, ctx, *, question: str):
		if ctx.message.author.voice.channel is None:
			return

		locale = config.getLocale(ctx.guild.id)
		channel = ctx.message.author.voice.channel

		sounds = os.listdir('{}/../sounds/magicShell/{}'.format(os.path.dirname(__file__), locale))
		if len(sounds) == 0:
			return

		sound = '{}/../sounds/magicShell/{}/{}'.format(os.path.dirname(__file__), locale,
													   sounds[random.randint(0, len(sounds) - 1)])

		try:
			voice_client = await channel.connect()
		except discord.ClientException:
			await ctx.send(config.strings[locale]['magicShell']['join_channel'])
		else:
			voice_client.play(discord.FFmpegPCMAudio(sound, options='-loglevel warning'))
			await asyncio.sleep(2)
			await voice_client.disconnect()


def setup(bot):
	bot.add_cog(MagicShell(bot))
