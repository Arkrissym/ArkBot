from discord.ext import commands
import config

class TestModule:
	def __init__(self, bot):
		self.bot=bot

	@commands.command(pass_context=True)
	async def test(self, ctx):
		counter=0
#		tmp = await ctx.send('Calculating messages...')
		tmp = await ctx.send(config.strings['testModule']['calc_messages'])
		async for log in ctx.message.channel.history(limit=1000):
			if log.author == ctx.message.author:
				if not self.bot.get_command(log.content[1:]):
					counter+=1

#		await tmp.edit(content='You have {} messages.'.format(counter))
		await tmp.edit(content=config.strings['testModule']['sum_messages'].format(counter))

	@commands.command(pass_context=True)
	async def echo(self, ctx, *, string : str):
		await ctx.send(string)

def setup(bot):
	bot.add_cog(TestModule(bot))
