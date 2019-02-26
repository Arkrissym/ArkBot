#MIT License

#Copyright (c) 2018-2019 Arkrissym

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
import discord

import asyncio
import os
import random

import config
from logger import logger as log

if not discord.opus.is_loaded():
	try:
		discord.opus.load_opus('opus')
	except:
		try:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so')
		except:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so.0')

class MagicShell(commands.Cog):
	def __init__(self, bot):
		self.bot=bot

	@commands.command(no_pm=True)
	async def shell(self, ctx, *, question : str):
		if ctx.message.author.voice.channel == None:
			return

		locale=config.getLocale(ctx.guild.id)
		channel=ctx.message.author.voice.channel

		sounds=os.listdir('{}/../sounds/magicShell/{}'.format(os.path.dirname(__file__), locale))
		if len(sounds) == 0:
			return

		sound='{}/../sounds/magicShell/{}/{}'.format(os.path.dirname(__file__), locale, sounds[random.randint(0, len(sounds)-1)])

		try:
			voice_client=await channel.connect()
		except discord.ClientException:
			await ctx.send(config.strings[locale]['magicShell']['join_channel'])
		else:
			voice_client.play(discord.FFmpegPCMAudio(sound, options='-loglevel warning'))
			await asyncio.sleep(2)
			await voice_client.disconnect()

def setup(bot):
	bot.add_cog(MagicShell(bot))
