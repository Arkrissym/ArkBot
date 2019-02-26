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
import time
import config

class Uptime(commands.Cog):
	def __init__(self):
		self.startTime=time.time()

	@commands.command()
	async def uptime(self, ctx):
		locale=config.getLocale(ctx.guild.id)

		answer=config.strings[locale]['uptime']['uptime_answer']
		uptime=time.time() - self.startTime

		days=0
		hours=0
		mins=0

		if uptime > 86400:
			days=uptime / 86400
			days=int(days)
			uptime-=days * 86400
			if days == 1:
				answer=answer + str(days) + config.strings[locale]['uptime']['day']
			else:
				answer=answer + str(days) + config.strings[locale]['uptime']['days']
		if uptime > 3600:
			hours=uptime / 3600
			hours=int(hours)
			uptime-=hours * 3600
			if days > 0:
				answer=answer + ', '
			if hours == 1:
				answer=answer + str(hours) + config.strings[locale]['uptime']['hour']
			else:
				answer=answer + str(hours) + config.strings[locale]['uptime']['hours']
		if uptime > 60:
			mins=uptime / 60
			mins=int(mins)
			uptime-=mins * 60
			if days > 0 or hours > 0:
				answer=answer + ', '
			if mins == 1:
				answer=answer + str(mins) + config.strings[locale]['uptime']['min']
			else:
				answer=answer + str(mins) + config.strings[locale]['uptime']['mins']

		if (days > 0 or hours > 0 or mins > 0) and (uptime > 0):
			answer=answer + ', '
		uptime=int(uptime)
		if uptime == 1:
			answer=answer + str(uptime) + config.strings[locale]['uptime']['sec']
		elif uptime > 1:
			answer=answer + str(uptime) + config.strings[locale]['uptime']['secs']

		answer=answer + '.'

		await ctx.send(answer)

def setup(bot):
	bot.add_cog(Uptime())
