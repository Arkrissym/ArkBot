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
import config

class Nickname:
	def __init__(self, bot):
		self.bot=bot
		#self.nameList=[
		#	'Noname',
		#	'Alphakevin',
		#	'Chantal',
		#	'Teemo',
		#	'Peter Müller, Klasse 2C',
		#	'Count Schoko',
		#	'Bob Ross',
		#	'Donald Trump',
		#	'Angela Merkel',
		#	'Barack Obama',
		#	'Zeuge Seehofas',
		#	'Karsten Stahl',
		#	'Hans Jörg'
		#]

		#self.fake=Faker(config.config['nickName']['Faker_locale'])

	#@commands.command(pass_context=True, hidden=True, no_pm=True)
	#async def yourmom(self, ctx):
	#	oldName=ctx.author.nick
	#	await ctx.author.edit(nick='Deine Mudda')
	#	await asyncio.sleep(20)
	#	await ctx.author.edit(nick=oldName)
	#	await ctx.message.delete()

	@commands.command(pass_context=True, no_pm=True)
	async def randomnick(self, ctx):
		#if random.randint(0, 2) < 1:
		#	await ctx.author.edit(nick=self.nameList[random.randint(0, len(nameList) - 1)])
		#else:
		await ctx.author.edit(nick=Faker(config.getLocale(ctx.guild.id)).name())

	@commands.command(pass_context=True, no_pm=True)
#	@commands.has_permissions(change_nickname=True)
	async def setnick(self, ctx, newNick : str=None):
		if newNick:
			await ctx.author.edit(nick=newNick)
		else:
			await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])

	@commands.command(pass_context=True, no_pm=True)
	async def idiot(self, ctx):
		await ctx.author.edit(nick=config.strings[config.getLocale(ctx.guild.id)]['nickName']['idiot'])

def setup(bot):
	bot.add_cog(Nickname(bot))
