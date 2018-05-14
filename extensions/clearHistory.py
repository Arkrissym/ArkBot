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
from datetime import datetime
import time
import asyncio

import config

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
			elif len(log.content) > 1 and log.content.startswith(config.getPrefix(ctx.guild_id.id)):
				if self.bot.get_command(log.content[len(config.getPrefix(ctx.guild_id.id)):]):
					msgs.append(log)

		await ctx.message.channel.delete_messages(msgs)

	@commands.command(pass_context=True, no_pm=True, description='tabularasa protocol')
	@commands.has_permissions(administrator=True)
	async def tabularasa(self, ctx):
		async for log in ctx.message.channel.history(limit=None):
			await log.delete()

def setup(bot):
	bot.add_cog(ClearHistory(bot))
