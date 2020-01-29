# MIT License
# see LICENSE for details

# Copyright (c) 2018-2019 Arkrissym


import asyncio
import os
import pathlib
import subprocess

import discord
import psycopg2
import youtube_dl
from discord.ext import commands
from psycopg2 import sql

from core import config
from core.logger import logger as log


class CustomCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.commands = {}
		self.voice_clients = set()

	@commands.Cog.listener()
	async def on_connect(self):
		for vc in self.voice_clients:
			try:
				await vc.disconnect()
			except Exception as e:
				log.error("customCommands (on_connect) - cannot disconnect from voice: {}".format(str(e)))

	@commands.Cog.listener()
	async def on_ready(self):
		if config.config["CustomCommands"]["download_audio"].lower() == "true":
			pathlib.Path("{}/../sounds/customCommands".format(os.path.dirname(__file__))).mkdir(parents=True,
																								exist_ok=True)

			for g in self.bot.guilds:
				#				log.info("checking guild: " + str(g))
				all_commands = {}
				tries = 0
				while all_commands == {} and tries < 30:
					all_commands = self.getCommands(g.id)
					if all_commands == {}:
						tries = tries + 1
						await asyncio.sleep(10)

				for command in all_commands.keys():
					try:
						if all_commands[command]["type"] == "music" and not str(g.id) in os.listdir(
								'{}/../sounds/customCommands'.format(os.path.dirname(__file__))) or not "{}.mp3".format(
							command) in os.listdir(
							'{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(g.id))):
							link_or_name = all_commands[command]["result"]

							ytdl_opts = {
								'format': 'webm[abr>0]/bestaudio/best',
								'prefer_ffmpeg': True,
								'default_search': 'ytsearch',
								'noplaylist': True,
								'quiet': True,
								'ignoreerrors': True,
								'logger': log
							}

							ytdl = youtube_dl.YoutubeDL(ytdl_opts)
							info = await self.bot.loop.run_in_executor(None, ytdl.extract_info, link_or_name, False)

							if "entries" in info:
								info = info['entries'][0]

							source = info['url']

							filename = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__),
																					  str(g.id), command)

							pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

							log.info("Downloading audio for command: " + command)
							await self.bot.loop.run_in_executor(None, subprocess.call,
																["ffmpeg", "-y", "-i", source, filename, "-loglevel",
																 "warning"])
						elif all_commands[command]["type"] == "user_audio" and not str(g.id) in os.listdir(
								'{}/../sounds/customCommands'.format(os.path.dirname(__file__))) or not "{}.mp3".format(
							command) in os.listdir(
							'{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(g.id))):
							filename = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__),
																					  str(g.id), command)

							await self.bot.loop.run_in_executor(None, subprocess.call,
																["ffmpeg", "-y", "-i", all_commands[command]["result"],
																 filename, "-loglevel", "warning"])
					except Exception as e:
						log.warning(str(e))

	def getCommands(self, guild_id):
		if str(guild_id) in self.commands.keys():
			return self.commands[str(guild_id)]

		try:
			conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="prefer")
			cur = conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
			cur.execute(sql.SQL("SELECT * FROM customCommands WHERE id = %s"), [str(guild_id)])

			ret = {}
			for row in cur:
				if row[0] == str(guild_id):
					ret[row[1]] = {
						"type": row[2],
						"result": row[3]
					}

			self.commands[str(guild_id)] = ret

			cur.close()
			conn.close()

			return ret
		except Exception as e:
			log.warning("customCommands - cannot read from database: %s", str(e))
			return {}

	def addCommand(self, guild_id, command, type, result):
		try:
			conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="prefer")
			cur = conn.cursor()

			cur.execute(sql.SQL("INSERT INTO customCommands VALUES (%s, %s, %s, %s)"),
						[str(guild_id), str(command), str(type), str(result)])

			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("customCommands - cannot write to database: %s", str(e))

		if str(guild_id) in self.commands.keys():
			self.commands[str(guild_id)][str(command)] = {
				"type": str(type),
				"result": str(result)
			}
		else:
			self.commands[str(guild_id)] = {
				str(command): {
					"type": str(type),
					"result": str(result)
				}
			}

	def deleteCommand(self, guild_id, command):
		try:
			conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="prefer")
			cur = conn.cursor()

			cur.execute(sql.SQL("DELETE FROM customCommands WHERE id = %s AND command = %s"),
						[str(guild_id), str(command)])

			conn.commit()

			cur.close()
			conn.close()
		except Exception as e:
			log.warning("customCommands - cannot delete from database: %s", str(e))

		del self.commands[str(guild_id)][str(command)]

	@commands.Cog.listener()
	async def on_message(self, message):
		if message.author.bot or message.guild == None or message.content.startswith(
				config.getPrefix(message.guild.id)) == False:
			return

		prefix_len = len(config.getPrefix(message.guild.id))
		all_commands = self.getCommands(message.guild.id)

		for command in all_commands.keys():
			if command == message.content[prefix_len:]:
				if all_commands[command]["type"] == "music":
					if message.author.voice.channel == None:
						continue

					if str(message.guild.id) in os.listdir(
							'{}/../sounds/customCommands'.format(os.path.dirname(__file__))) and "{}.mp3".format(
						command) in os.listdir(
						'{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(message.guild.id))):
						source = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__),
																				str(message.guild.id), command)
					else:
						ytdl_opts = {
							'format': 'webm[abr>0]/bestaudio/best',
							'prefer_ffmpeg': True,
							'default_search': 'ytsearch',
							'noplaylist': True,
							'quiet': True,
							'ignoreerrors': True,
							'logger': log
						}

						ytdl = youtube_dl.YoutubeDL(ytdl_opts)
						info = await self.bot.loop.run_in_executor(None, ytdl.extract_info,
																   all_commands[command]["result"], False)
						if "entries" in info:
							info = info['entries'][0]

						source = info['url']

					voice_client = None
					try:
						voice_client = await message.author.voice.channel.connect()
						self.voice_clients.add(voice_client)
					except discord.ClientException:
						await message.channel.send(
							config.strings[config.getLocale(message.channel.guild.id)]['customCommands'][
								'join_channel'])
					else:
						voice_client.play(
							discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source,
																				options='-loglevel warning -af loudnorm=i=-23.0:lra=7.0:tp=-2.0:offset=0.0:measured_i=-9.11:measured_lra=3.5:measured_tp=-0.03:measured_thresh=-19.18:linear=true[norm0]'),
														 volume=0.8))
						while voice_client.is_playing():
							await asyncio.sleep(0.2)
						await asyncio.sleep(1)

					if voice_client:
						await voice_client.disconnect()
						self.voice_clients.remove(voice_client)
				elif all_commands[command]["type"] == "user_audio":
					if str(message.guild.id) in os.listdir(
							'{}/../sounds/customCommands'.format(os.path.dirname(__file__))) and "{}.mp3".format(
						command) in os.listdir(
						'{}/../sounds/customCommands/{}'.format(os.path.dirname(__file__), str(message.guild.id))):
						source = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__),
																				str(message.guild.id), command)
					else:
						source = all_commands[command]["result"]

					voice_client = None
					try:
						voice_client = await message.author.voice.channel.connect()
					except discord.ClientException:
						await message.channel.send(
							config.strings[config.getLocale(message.channel.guild.id)]['customCommands'][
								'join_channel'])
					else:
						voice_client.play(
							discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source,
																				options='-loglevel warning -af loudnorm=i=-23.0:lra=7.0:tp=-2.0:offset=0.0:measured_i=-9.11:measured_lra=3.5:measured_tp=-0.03:measured_thresh=-19.18:linear=true[norm0]'),
														 volume=0.8))
						while voice_client.is_playing():
							await asyncio.sleep(0.1)
						await asyncio.sleep(1)

					if voice_client:
						await voice_client.disconnect()
				else:  # text
					await message.channel.send(all_commands[command]["result"])

	@commands.command(no_pm=True, help="customCommands+list_commands_help")
	async def list_commands(self, ctx):
		text = ""
		for command_name in self.getCommands(ctx.guild.id).keys():
			text = text + "\n" + command_name

		if text == "":
			text = config.strings[config.getLocale(ctx.guild.id)]["customCommands"]["no_commands"]

		# embed=discord.Embed(title=config.strings[config.getLocale(ctx.guild.id)]["customCommands"]["list_commands"], description=text)
		embed = discord.Embed(description=text)
		await ctx.send(embed=embed)

	@commands.command(no_pm=True, brief="customCommands+delete_command_brief",
					  help="customCommands+delete_command_help")
	@config.is_admin_or_owner()
	async def delete_command(self, ctx, command: str):
		if not command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(
				config.strings[config.getLocale(ctx.guild.id)]['customCommands']['command_doesnt_exist'].format(
					command))
			return

		await ctx.bot.loop.run_in_executor(None, self.deleteCommand, ctx.guild.id, command)

		try:
			os.remove(
				'{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(ctx.guild.id), command))
		except:
			pass

		await ctx.send(
			config.strings[config.getLocale(ctx.guild.id)]['customCommands']['delete_command'].format(command))

	@commands.command(no_pm=True, brief="customCommands+add_text_command_brief",
					  help="customCommands+add_text_command_help")
	@config.is_admin_or_owner()
	async def add_text_command(self, ctx, command: str, *, answer: str):
		if command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(
				config.strings[config.getLocale(ctx.guild.id)]['customCommands']['command_exists'].format(command))
			return

		await ctx.bot.loop.run_in_executor(None, self.addCommand, ctx.guild.id, command, "text", answer)
		await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['customCommands']['add_command'].format(command))

	@commands.command(no_pm=True, brief="customCommands+add_music_command_brief",
					  help="customCommands+add_music_command_help")
	@config.is_admin_or_owner()
	async def add_music_command(self, ctx, command: str, *, link_or_name: str = None):
		locale = config.getLocale(ctx.guild.id)

		if command in self.getCommands(ctx.guild.id).keys():
			await ctx.send(config.strings[locale]['customCommands']['command_exists'].format(command))
			return

		if link_or_name == None:
			if len(ctx.message.attachments) == 0:
				await ctx.send(config.strings[locale]["customCommands"]["no_audio_file_or_link"])
				return

			audio_url = ctx.message.attachments[0].url

			# log.info(audio_url)

			if config.config["CustomCommands"]["download_audio"].lower() == "true":
				filename = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(ctx.guild.id),
																		  command)

				log.info("Downloading audio for command: " + command)
				await ctx.bot.loop.run_in_executor(None, subprocess.call,
												   ["ffmpeg", "-y", "-i", audio_url, filename, "-loglevel", "warning"])

			await ctx.bot.loop.run_in_executor(None, self.addCommand, ctx.guild.id, command, "user_audio", audio_url)
		else:
			if config.config["CustomCommands"]["download_audio"].lower() == "true":
				ytdl_opts = {
					'format': 'webm[abr>0]/bestaudio/best',
					'prefer_ffmpeg': True,
					'default_search': 'ytsearch',
					'noplaylist': True,
					'quiet': True,
					'ignoreerrors': True,
					'logger': log
				}

				ytdl = youtube_dl.YoutubeDL(ytdl_opts)
				info = await self.bot.loop.run_in_executor(None, ytdl.extract_info, link_or_name, False)

				if "entries" in info:
					info = info['entries'][0]

				if "is_live" in info and info["is_live"] == True:
					await ctx.send(config.strings[locale]["customCommands"]["warn_live"])
					return

				source = info['url']

				filename = '{}/../sounds/customCommands/{}/{}.mp3'.format(os.path.dirname(__file__), str(ctx.guild.id),
																		  command)

				log.info("Downloading audio for command: " + command)
				pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

				await ctx.bot.loop.run_in_executor(None, subprocess.call,
												   ["ffmpeg", "-y", "-i", source, filename, "-loglevel", "warning"])

			await ctx.bot.loop.run_in_executor(None, self.addCommand, ctx.guild.id, command, "music", link_or_name)

		await ctx.send(config.strings[locale]['customCommands']['add_command'].format(command))


def setup(bot):
	bot.add_cog(CustomCommands(bot))
