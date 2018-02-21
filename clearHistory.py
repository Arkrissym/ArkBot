from discord.ext import commands
from datetime import datetime
import time
import asyncio

class ClearHistory:
	def __init__(self, bot):
		self.bot=bot

	@commands.command(pass_context=True, no_pm=True)
	@commands.has_permissions(manage_messages=True)
	async def clearlog(self, ctx):
		msgs=[]
		async for log in ctx.message.channel.history(limit=None, after=datetime.utcfromtimestamp(time.time()-86400)):
			if log.author == self.bot.user:
				msgs.append(log)
			elif len(log.content) > 1:
				if self.bot.get_command(log.content[1:]):
					msgs.append(log)

		await ctx.message.channel.delete_messages(msgs)

	@commands.command(pass_context=True, no_pm=True, description='tabularasa protocol')
	@commands.has_permissions(administrator=True)
	async def tabularasa(self, ctx):
		async for log in ctx.message.channel.history(limit=None):
			await log.delete()

def setup(bot):
	bot.add_cog(ClearHistory(bot))
