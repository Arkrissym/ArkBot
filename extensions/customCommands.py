#MIT License

#Copyright (c) 2018 Arkrissym

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

import discord
from discord.ext import commands

from logger import logger as log
import config

import os
import psycopg2
from psycopg2 import sql
import youtube_dl
import asyncio
import subprocess
import pathlib

if not discord.opus.is_loaded():
	try:
		discord.opus.load_opus('opus')
	except:
		try:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so')
		except:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so.0')

class CustomCommands:
	def __init__(self, bot):
		self.bot=bot
		self.commands={}

	async def on_ready(self):
		if config.config["CustomCommands"]["download_audio"].lower() == "true":
			for g in self.bot.guilds:
				all_commands=getCommands(g.id)
				for commmand in all_commands.keys():
					if all_commands[command]["type"] == "music" and not "{}.mp3".format(command) in os.listdir('{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(g.id))):
						link_or_name=all_commands[command]["result"]
						
						ytdl_opts={
							'format': 'webm[abr>0]/bestaudio/best',
							'prefer_ffmpeg': True,
							'default_search': 'ytsearch',
							'noplaylist': True,
							'quiet': True,
							'ignoreerrors' : True,
							'logger': log
						}

						ytdl=youtube_dl.YoutubeDL(ytdl_opts)
						info=await ctx.bot.loop.run_in_executor(None, ytdl.extract_info, link_or_name, False)

						if "entries" in info:
							info=info['entries'][0]

#						if "is_live" in info and info["is_live"] == True:
#							return

						source=info['url']
						duration=info['duration']
		
						filename='{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(g.id), command)

						log.info("Downloading audio for command: " + command)
						pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
		
						await ctx.bot.loop.run_in_executor(None, subprocess.call, ["ffmpeg", "-y", "-i" , source, filename, "-loglevel", "warning"])
						with open('{}/../sounds/customCommands/{}/{}_duration.txt'.format(os.path.dirname(__file__), str(g.id), command), "w") as file:
							file.write(str(duration) + "\n")
							file.close()

	def getCommands(self, guild_id):
		if str(guild_id) in self.commands.keys():
			return self.commands[str(guild_id)]

		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
			cur.execute(sql.SQL("SELECT * FROM customCommands WHERE id = %s"), [str(guild_id)])

			ret = {}
			for row in cur:
				if row[0] == str(guild_id):
					ret[row[1]]={
						"type" : row[2],
						"result" : row[3]
						}

			self.commands[str(guild_id)]=ret

			cur.close()
			conn.close()

			return ret
		except Exception as e:
			log.warning("customCommands - cannot read from database: %s", str(e))
			return {}

	def addCommand(self, guild_id, command, type, result):
		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor()

			cur.execute(sql.SQL("INSERT INTO customCommands VALUES (%s, %s, %s, %s)"), [str(guild_id), str(command), str(type), str(result)])

			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("customCommands - cannot write to database: %s", str(e))

		if str(guild_id) in self.commands.keys():
			self.commands[str(guild_id)][str(command)]={
				"type" : str(type),
				"result" : str(result)
				}
		else:
			self.commands[str(guild_id)]={
				str(command) : {
					"type" : str(type),
					"result" : str(result)
					}
				}

	def deleteCommand(self, guild_id, command):
		try:
			conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
			cur=conn.cursor()

			cur.execute(sql.SQL("DELETE FROM customCommands WHERE id = %s AND command = %s"), [str(guild_id), str(command)])

			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("customCommands - cannot delete from database: %s", str(e))

		del self.commands[str(guild_id)][str(command)]

	async def on_message(self, message):
		if message.author.bot or message.guild == None or message.content.startswith(config.getPrefix(message.guild.id)) == False:
			return

		prefix_len=len(config.getPrefix(message.guild.id))
		all_commands=self.getCommands(message.guild.id)
#		print(all_commands)

		for command in all_commands.keys():
			if command == message.content[prefix_len:]:
				if all_commands[command]["type"] == "music":
					if message.author.voice.channel == None:
						continue

					if "{}.mp3".format(command) in os.listdir('{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(message.guild.id))):
						source='{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(message.guild.id), command)
						try:
							with open('{}/../sounds/customCommands/{}/{}_duration.txt'.format(os.path.dirname(__file__), str(message.guild.id), command), "r") as file:
								duration=int(file.readline())
								file.close()
						except:
							duration=10
					else:
						ytdl_opts={
							'format': 'webm[abr>0]/bestaudio/best',
							'prefer_ffmpeg': True,
							'default_search': 'ytsearch',
							'noplaylist': True,
							'quiet': True,
							'ignoreerrors' : True,
							'logger': log
						}

						ytdl=youtube_dl.YoutubeDL(ytdl_opts)
						info=await self.bot.loop.run_in_executor(None, ytdl.extract_info, all_commands[command]["result"], False)
						if "entries" in info:
							info=info['entries'][0]

						source=info['url']
						duration=info['duration']
#						print(duration)

					voice_client=None
					try:
						voice_client=await message.author.voice.channel.connect()
					except discord.ClientException:
						await message.channel.send(config.strings[config.getLocale(message.channel.guild.id)]['customCommands']['join_channel'])
					else:
						voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source, options='-loglevel warning'), volume=0.8))
						await asyncio.sleep(duration+1)

					if voice_client:
						await voice_client.disconnect()
				else: #text
					await message.channel.send(all_commands[command]["result"])

	@commands.command(pass_context=True, no_pm=True, brief="customCommands+delete_command_brief", help="customCommands+delete_command_help")
	@commands.has_permissions(administrator=True)
	async def delete_command(self, ctx, command : str):
		if not command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['command_doesnt_exist'].format(command))
			return

		await ctx.bot.loop.run_in_executor(None, self.deleteCommand, ctx.guild.id, command)
		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['delete_command'].format(command))

	@commands.command(pass_context=True, no_pm=True, brief="customCommands+add_text_command_brief", help="customCommands+add_text_command_help")
	@commands.has_permissions(administrator=True)
	async def add_text_command(self, ctx, command : str, *, answer : str):
		if command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['command_exists'].format(command))
			return

		await ctx.bot.loop.run_in_executor(None, self.addCommand, ctx.guild.id, command, "text", answer)
		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['add_command'].format(command))

	@commands.command(pass_context=True, no_pm=True, brief="customCommands+add_music_command_brief", help="customCommands+add_music_command_help")
	@commands.has_permissions(administrator=True)
	async def add_music_command(self, ctx, command : str, *, link_or_name : str):
		if command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['command_exists'].format(command))
			return

		if config.config["CustomCommands"]["download_audio"].lower() == "true":
			ytdl_opts={
				'format': 'webm[abr>0]/bestaudio/best',
				'prefer_ffmpeg': True,
				'default_search': 'ytsearch',
				'noplaylist': True,
				'quiet': True,
				'ignoreerrors' : True,
				'logger': log
			}

			ytdl=youtube_dl.YoutubeDL(ytdl_opts)
			info=await self.bot.loop.run_in_executor(None, ytdl.extract_info, link_or_name, False)

			if "entries" in info:
				info=info['entries'][0]

			if "is_live" in info and info["is_live"] == True:
				await ctx.send(config.strings["customCommands"]["warn_live"])
				return

			source=info['url']
			duration=info['duration']
		
			filename='{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(ctx.guild.id), command)

			log.info("Downloading audio for command: " + command)
			pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
		
			await ctx.bot.loop.run_in_executor(None, subprocess.call, ["ffmpeg", "-y", "-i" , source, filename, "-loglevel", "warning"])
			with open('{}/../sounds/customCommands/{}/{}_duration.txt'.format(os.path.dirname(__file__), str(ctx.guild.id), command), "w") as file:
				file.write(str(duration) + "\n")
				file.close()

		await ctx.bot.loop.run_in_executor(None, self.addCommand, ctx.guild.id, command, "music", link_or_name)
		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['add_command'].format(command))

def setup(bot):
	bot.add_cog(CustomCommands(bot))
