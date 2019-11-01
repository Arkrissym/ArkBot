# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym

import time

from discord.ext import commands

from core import config


class Uptime(commands.Cog):
	def __init__(self):
		self.startTime = time.time()

	@commands.command()
	async def uptime(self, ctx):
		locale = config.getLocale(ctx.guild.id)

		answer = config.strings[locale]['uptime']['uptime_answer']
		uptime = time.time() - self.startTime

		days = 0
		hours = 0
		mins = 0

		if uptime > 86400:
			days = uptime / 86400
			days = int(days)
			uptime -= days * 86400
			if days == 1:
				answer = answer + str(days) + config.strings[locale]['uptime']['day']
			else:
				answer = answer + str(days) + config.strings[locale]['uptime']['days']
		if uptime > 3600:
			hours = uptime / 3600
			hours = int(hours)
			uptime -= hours * 3600
			if days > 0:
				answer = answer + ', '
			if hours == 1:
				answer = answer + str(hours) + config.strings[locale]['uptime']['hour']
			else:
				answer = answer + str(hours) + config.strings[locale]['uptime']['hours']
		if uptime > 60:
			mins = uptime / 60
			mins = int(mins)
			uptime -= mins * 60
			if days > 0 or hours > 0:
				answer = answer + ', '
			if mins == 1:
				answer = answer + str(mins) + config.strings[locale]['uptime']['min']
			else:
				answer = answer + str(mins) + config.strings[locale]['uptime']['mins']

		if (days > 0 or hours > 0 or mins > 0) and (uptime > 0):
			answer = answer + ', '
		uptime = int(uptime)
		if uptime == 1:
			answer = answer + str(uptime) + config.strings[locale]['uptime']['sec']
		elif uptime > 1:
			answer = answer + str(uptime) + config.strings[locale]['uptime']['secs']

		answer = answer + '.'

		await ctx.send(answer)


def setup(bot):
	bot.add_cog(Uptime())
