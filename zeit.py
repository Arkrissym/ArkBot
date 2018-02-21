from discord.ext import commands
import random

class Time:
	def __init__(self, bot):
		self.bot=bot
		self.list=[
			'Der Zeiger liegt in der Kurve.',
			'Es ist kurz vor knapp.',
			'Nur noch ein Tag, dann ist morgen.',
			'Zu spät...'
		]
		self.triggers=[
			'Wie spät ist es?'
		]

	@commands.command(pass_context=True, aliases=['zeit'])
	async def time(self, ctx):
		await ctx.send(self.list[random.randint(0, len(self.list) - 1)])

	async def on_message(self, message):
		for trig in self.triggers:
			if message.content == trig:
				await message.channel.send(self.list[random.randint(0, len(self.list) - 1)])


def setup(bot):
	bot.add_cog(Time(bot))
