from discord.ext import commands
import time
import config

class Uptime:
	def __init__(self, bot):
		self.bot=bot
		self.startTime=time.time()

	@commands.command(pass_context=True)
	async def uptime(self, ctx):
		answer='Non-stop aktiv seit '
		uptime=time.time() - self.startTime

		days=0
		hours=0
		mins=0

		if uptime > 86400:
			days=uptime / 86400
			days=int(days)
			uptime-=days * 86400
			if days == 1:
				answer=answer + str(days) + config.strings['uptime']['day']
			else:
				answer=answer + str(days) + config.strings['uptime']['days']
		if uptime > 3600:
			hours=uptime / 3600
			hours=int(hours)
			uptime-=hours * 3600
			if days > 0:
				answer=answer + ', '
			if hours == 1:
				answer=answer + str(hours) + config.strings['uptime']['hour']
			else:
				answer=answer + str(hours) + config.strings['uptime']['hours']
		if uptime > 60:
			mins=uptime / 60
			mins=int(mins)
			uptime-=mins * 60
			if days > 0 or hours > 0:
				answer=answer + ', '
			if mins == 1:
				answer=answer + str(mins) + config.strings['uptime']['min']
			else:
				answer=answer + str(mins) + config.strings['uptime']['mins']

		if (days > 0 or hours > 0 or mins > 0) and (uptime > 0):
			answer=answer + ', '
		uptime=int(uptime)
		if uptime == 1:
			answer=answer + str(uptime) + config.strings['uptime']['sec']
		elif uptime > 1:
			answer=answer + str(uptime) + config.strings['uptime']['secs']

		answer=answer + '.'

		await ctx.send(answer)

def setup(bot):
	bot.add_cog(Uptime(bot))
