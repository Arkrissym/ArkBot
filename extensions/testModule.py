# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import discord
from discord.ext import commands

from core import config
from core.logger import logger


class TestModule(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def test(self, ctx):
		counter = 0

		locale = config.getLocale(ctx.guild.id)
		if ctx.guild:
			prefix = config.getPrefix(ctx.guild.id)
		else:
			prefix = config.config['bot']['cmd_prefix']

		tmp = await ctx.send(config.strings[locale]['testModule']['calc_messages'])
		async for log in ctx.message.channel.history(limit=1000):
			if log.author == ctx.message.author:
				cmd = None
				if ctx.message.content.startswith(prefix):
					cmd = ctx.bot.get_command(ctx.message.content[len(prefix):])

				if cmd is None:
					counter += 1

		await tmp.edit(content=config.strings[locale]['testModule']['sum_messages'].format(counter))

	@commands.command(help="echo_help", usage="<string>", brief="testModule+echo_brief")
	async def echo(self, ctx, *, string: str):
		await ctx.send(string)

	@commands.command(brief="Send an Embed.")
	async def embed(self, ctx):
		embed = discord.Embed(title='Title', description='description', color=0x00ff00)
		embed.set_thumbnail(url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.set_author(name='ArkBot', url='https://github.com/Arkrissym/ArkBot',
						 icon_url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.add_field(name='name1', value='value1', inline=True)
		embed.add_field(name='name2', value='value2', inline=True)
		embed.add_field(name='name3', value='value3', inline=False)
		embed.add_field(name='name4', value='value4', inline=False)
		embed.set_image(url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.set_footer(text='footer',
						 icon_url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')

		await ctx.send(embed=embed)

	@commands.command()
	async def prefix(self, ctx):
		await ctx.send(ctx.prefix)

	@commands.Cog.listener()
	async def on_message(self, message):
		# check, if message has been sent by a bot
		if message.author.bot:
			return

		cmd = None

		if (message.guild is not None) and message.content.startswith(config.getPrefix(message.guild.id)):
			cmd = self.bot.get_command(message.content[len(config.getPrefix(message.guild.id)):])
		elif message.content.startswith(config.config['bot']['cmd_prefix']):
			cmd = self.bot.get_command(message.content[len(config.config['bot']['cmd_prefix']):])

		if cmd:
			logger.info('command ' + cmd.name + ' called.')


def setup(bot):
	bot.add_cog(TestModule(bot))
