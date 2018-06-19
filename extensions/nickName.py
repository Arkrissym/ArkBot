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
import discord
import asyncio
import random
from faker import Faker
from faker.config import AVAILABLE_LOCALES
import config

class Nickname:
	@commands.command(pass_context=True, no_pm=True)
	async def randomnick(self, ctx):
		locale=config.getLocale(ctx.guild.id)
		if locale in AVAILABLE_LOCALES:
			await ctx.author.edit(nick=Faker(locale).name())
		else:
			await ctx.author.edit(nick=Faker().name())

	@commands.command(pass_context=True, no_pm=True)
	async def setnick(self, ctx, newNick : str=None):
		if newNick:
			await ctx.author.edit(nick=newNick)
		else:
			await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])

	@commands.command(pass_context=True, no_pm=True)
	async def idiot(self, ctx):
		await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])

def setup(bot):
	bot.add_cog(Nickname())
