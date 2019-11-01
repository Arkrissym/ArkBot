# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import random

from discord.ext import commands

from core import config


class Time(commands.Cog):
	@commands.command()
	async def time(self, ctx):
		answers = config.strings[config.getLocale(ctx.guild.id)]['zeit']['time_answers']
		await ctx.send(answers[random.randint(0, len(answers) - 1)])

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.guild:
			locale = config.getLocale(message.guild.id)
			answers = config.strings[locale]['zeit']['time_answers']
			triggers = config.strings[locale]['zeit']['time_triggers']

			for trig in triggers:
				if message.content == trig:
					await message.channel.send(answers[random.randint(0, len(answers) - 1)])


def setup(bot):
	bot.add_cog(Time())
