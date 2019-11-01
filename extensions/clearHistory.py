# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import time
from datetime import datetime

from discord.ext import commands

from core import config


class ClearHistory(commands.Cog):
	@commands.command(no_pm=True)
	@commands.has_permissions(manage_messages=True)
	async def clearlog(self, ctx):
		prefix = config.getPrefix(ctx.guild.id)
		prefix_len = len(prefix)

		msgs = []
		async for log in ctx.message.channel.history(limit=None, after=datetime.utcfromtimestamp(time.time() - 86400)):
			if len(msgs) == 100:
				await ctx.message.channel.delete_messages(msgs)
				msgs.clear()

			if log.author == ctx.bot.user:
				msgs.append(log)
			elif len(log.content) > 1 and log.content.startswith(prefix):
				if ctx.bot.get_command(log.content[prefix_len:]):
					msgs.append(log)

		if len(msgs) > 0:
			await ctx.message.channel.delete_messages(msgs)

	@commands.command(no_pm=True, description='tabularasa protocol')
	@config.is_admin_or_owner()
	async def tabularasa(self, ctx):
		async for log in ctx.message.channel.history(limit=None):
			await log.delete()


def setup(bot):
	bot.add_cog(ClearHistory())
