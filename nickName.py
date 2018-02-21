from discord.ext import commands
import discord
import asyncio
import random
from faker import Faker

class Nickname:
	def __init__(self, bot):
		self.bot=bot
		self.nameList=[
			'Noname',
			'Alphakevin',
			'Chantal',
			'Teemo',
			'Peter Müller, Klasse 2C',
			'Count Schoko',
			'Bob Ross',
			'Donald Trump',
			'Angela Merkel',
			'Barack Obama',
			'Zeuge Seehofas',
			'Karsten Stahl',
			'Hans Jörg'
		]

		self.fake=Faker('de_DE')

	@commands.command(hidden=True, no_pm=True)
	async def yourmom(self, ctx):
		oldName=ctx.author.nick
		await ctx.author.edit(nick='Deine Mudda')
		await asyncio.sleep(20)
		await ctx.author.edit(nick=oldName)
		await ctx.message.delete()

	@commands.command(no_pm=True)
	async def randomnick(self, ctx):
		if random.randint(0, 2) < 1:
			await ctx.author.edit(nick=self.nameList[random.randint(0, len(nameList) - 1)])
		else:
			await ctx.author.edit(nick=self.fake.name())

	@commands.command(no_pm=True)
#	@commands.has_permissions(change_nickname=True)
	async def setnick(self, ctx, newNick : str):
		if newNick:
			await ctx.author.edit(nick=newNick)
		else:
			await ctx.author.edit(nick='Ostfriese des Monats')

def setup(bot):
	bot.add_cog(Nickname(bot))
