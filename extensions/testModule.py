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

	@commands.command(pass_context=True)
	async def embed(self, ctx):
		embed=discord.Embed(title='Title', description='description', color=0x00ff00)
		embed.set_thumbnail(url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.set_author(name='ArkBot', url='https://github.com/Arkrissym/ArkBot', icon_url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.add_field(name='name1', value='value1', inline=True)
		embed.add_field(name='name2', value='value2', inline=True)
		embed.add_field(name='name3', value='value3', inline=False)
		embed.add_field(name='name4', value='value4', inline=False)
		embed.set_image(url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')
		embed.set_footer(text='footer', icon_url='https://cdn.pixabay.com/photo/2016/02/22/00/25/robot-1214536_960_720.png')

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(TestModule(bot))