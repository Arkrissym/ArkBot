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
import random
import config

class Time:
	@commands.command(pass_context=True)
	async def time(self, ctx):
		list=config.strings[config.getLocale(ctx.guild.id)]['zeit']['time_answers']
		await ctx.send(list[random.randint(0, len(list) - 1)])

	async def on_message(self, message):
		if message.guild:
			locale=config.getLocale(message.guild.id)
			list=config.strings[locale]['zeit']['time_answers']
			triggers=config.strings[locale]['zeit']['time_triggers']
			
			for trig in triggers:
				if message.content == trig:
					await message.channel.send(list[random.randint(0, len(list) - 1)])


def setup(bot):
	bot.add_cog(Time())
