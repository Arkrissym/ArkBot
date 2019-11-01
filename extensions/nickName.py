# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


from discord.ext import commands
from faker import Faker
from faker.config import AVAILABLE_LOCALES

from core import config


class Nickname(commands.Cog):
	@commands.command(no_pm=True)
	async def randomnick(self, ctx):
		locale = config.getLocale(ctx.guild.id)
		if locale in AVAILABLE_LOCALES:
			await ctx.author.edit(nick=Faker(locale).name())
		else:
			await ctx.author.edit(nick=Faker().name())

	@commands.command(no_pm=True)
	async def setnick(self, ctx, *, nick: str = None):
		if nick:
			await ctx.author.edit(nick=nick)
		else:
			await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])

	@commands.command(no_pm=True)
	async def idiot(self, ctx):
		await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])


def setup(bot):
	bot.add_cog(Nickname())
