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
from logger import logger as log

import random
import asyncio
import time
import os
import psycopg2
from psycopg2 import sql

class MulticolorRole:
	def __init__(self, bot):
		self.bot=bot
		self.config={}
		self.timer={}
		self.color_changer=self.bot.loop.create_task(self.color_changer_task())

	async def color_changer_task(self):
		log.info("starting color_changer_task")
		while True:
			l=await self.bot.loop.run_in_executor(None, self.change_color)
			for c in l:
				try:
					await c
				except Exception as e:
					log.warning("await c: {}".format(str(e)))
			await asyncio.sleep(1)

	def change_color(self):
		l=[]

		for guild in self.bot.guilds:
			try:
				if not str(guild.id) in self.timer.keys():
					self.timer[str(guild.id)]=time.time()-10

				role_id=self.getRoleId(guild.id)
				if role_id and time.time() > self.timer[str(guild.id)]:
					interval=self.getInterval(guild.id)

					role=discord.utils.get(guild.roles, id=role_id)

					r=random.randint(10, 255)
					g=random.randint(10, 255)
					b=random.randint(10, 255)

					coro=role.edit(color=discord.Color.from_rgb(r, g, b))
					l.append(coro)

					self.timer[str(guild.id)]=time.time()+interval
			except Exception as e:
				log.warning("change_color: {}".format(str(e)))

		return l

	def getConfig(self, guild_id):
		if str(guild_id) in self.config.keys():
			return [guild_id, self.config[str(guild_id)]["role_id"], self.config[str(guild_id)]["interval"]]

		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
			cur.execute(sql.SQL("SELECT * FROM multicolor_config WHERE id = %s"), [str(guild_id)])

			ret = None
			for row in cur:
				if row[0] == str(guild_id):
					ret = row
					self.config[str(guild_id)]={
						"role_id" : int(ret[1]),
						"interval" : int(ret[2])
						}

			cur.close()
			conn.close()

			return ret
		except Exception as e:
			log.warning("multicolorRole - cannot read from database: %s", str(e))
			return None

	def setConfig(self, guild_id, role_id, interval):
		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor()

			old = self.getConfig(guild_id)
			if old == None:
				cur.execute(sql.SQL("INSERT INTO multicolor_config VALUES (%s, %s, %s)"), [str(guild_id), str(role_id), str(interval)])
			else:
				cur.execute(sql.SQL("UPDATE multicolor_config SET id = %s, role_id = %s, interval = %s WHERE id = %s"), [str(guild_id), str(role_id), str(interval), str(guild_id)])	
	
			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("multicolorRole - cannot write to database: %s", str(e))

		self.config[str(guild_id)]={
			"role_id" : int(role_id),
			"interval" : int(interval)
			}

	def deleteConfig(self, guild_id):
		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor()

			cur.execute(sql.SQL("DELETE FROM multicolor_config WHERE id = %s)"), [str(guild_id)])
			
			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("multicolorRole - cannot delete from database: %s", str(e))

		del self.config[str(guild_id)]

	def getRoleId(self, guild_id):
		try:
			data=self.getConfig(guild_id)
		except:
			return None
		
		if data != None:
			return data[1]

		return None

	def getInterval(self, guild_id):
		try:
			data=self.getConfig(guild_id)
		except:
			return 10

		if data != None:
			return data[2]

		return 10

	@commands.command(pass_context=True, no_pm=True)
	async def multicolor_role(self, ctx, *, role : discord.Role):
		await self.bot.loop.run_in_executor(None, self.setConfig, ctx.guild.id, role.id, self.getInterval(ctx.guild.id))

		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]["multicolorRole"]["set_role"].format(str(role)))

	@commands.command(pass_context=True, no_pm=True)
	async def multicolor_interval(self, ctx, *, sec : int):
		if sec < 1:
			sec=1
		await self.bot.loop.run_in_executor(None, self.setConfig, ctx.guild.id, self.getRoleId(ctx.guild.id), sec)

		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]["multicolorRole"]["set_interval"].format(sec))

	@commands.command(pass_context=True, no_pm=True)
	async def disable_multicolor(self, ctx):
		await self.bot.loop.run_in_executor(None, self.deleteConfig, ctx.guild.id)
		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]["multicolorRole"]["disabled"])
	
def setup(bot):
	bot.add_cog(MulticolorRole(bot))
