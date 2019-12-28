# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import asyncio
import collections
import os
import pathlib
import random
import re
import subprocess
import time

import discord
import psycopg2
import youtube_dl
from discord.ext import commands
from psycopg2 import sql

from core import config, dataBase
from core.logger import logger as log

if not discord.opus.is_loaded():
	try:
		discord.opus.load_opus('opus')
	except Exception as e:
		log.fatal("music - Failed to load opus lib")
		raise e

_config = {}


def getConfig(id):
	if str(id) in _config.keys():
		return [id, _config[str(id)]["queue_mode"], _config[str(id)]["loop"]]

	try:
		conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="prefer")
		cur = conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
		cur.execute(sql.SQL("SELECT * FROM music_config WHERE id = %s"), [str(id)])

		ret = None
		for row in cur:
			if row[0] == str(id):
				ret = row
				_config[str(id)] = {
					"queue_mode": ret[1],
					"loop": ret[2]
				}

		cur.close()
		conn.close()

		return ret
	except Exception as e:
		log.warning("music - cannot read from database: %s", str(e))
		return None


def setConfig(id, queue_mode, loop):
	try:
		conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="prefer")
		cur = conn.cursor()

		old = getConfig(id)
		if old == None:
			cur.execute(sql.SQL("INSERT INTO music_config VALUES (%s, %s, %s)"), [str(id), queue_mode, loop])
		else:
			cur.execute(sql.SQL("UPDATE music_config SET id = %s, queue_mode = %s, loop = %s WHERE id = %s"),
						[str(id), queue_mode, loop, str(id)])

		conn.commit()

		cur.close()
		conn.close()
	except Exception as e:
		log.warning("music - cannot write to database: %s", str(e))

	_config[str(id)] = {
		"queue_mode": queue_mode,
		"loop": loop
	}


def getQueueMode(id):
	try:
		data = getConfig(id)
	except:
		return "normal"

	if data != None:
		return data[1]

	return "normal"


def getLoopMode(id):
	try:
		data = getConfig(id)
	except:
		return "off"

	if data != None:
		return data[2]

	return "off"


class VoiceEntry:
	def __init__(self, requester, channel, song_name, url, thumbnail_url, uploader, id):
		self.requester = requester
		self.channel = channel
		self.name = song_name
		self.url = url
		self.thumbnail_url = thumbnail_url
		self.uploader = uploader
		self.id = id


class VoiceState:
	def __init__(self, bot):
		self.bot = bot
		self.current_song = None
		self.previous_song = None
		self.voice_client = None
		self.voice_channel = None
		self.songs = collections.deque(maxlen=1000)
		self.play_next_song = asyncio.Event()
		self.audio_player = self.bot.loop.create_task(self.audio_player_task())

	def skip(self):
		self.voice_client.stop()

	async def stop(self):
		if len(self.songs) > 0:
			self.songs.clear()
		await self.voice_client.disconnect()
		self.voice_channel = None
		self.current_song = None
		self.previous_song = None

	def pause(self):
		self.voice_client.pause()

	def resume(self):
		self.voice_client.resume()

	def is_playing(self):
		return self.voice_client.is_playing()

	def play_next(self, error):
		self.previous_song = self.current_song
		self.current_song = None
		self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

	async def audio_player_task(self):
		while True:
			self.play_next_song.clear()

			wait = True
			while wait:
				if self.voice_client is not None:
					if self.voice_client.is_connected():
						wait = False
				await asyncio.sleep(1.0)

			if getLoopMode(self.voice_channel.guild.id) == "on" and self.previous_song is not None:
				self.songs.append(self.previous_song)

			while len(self.songs) == 0:
				await asyncio.sleep(1.0)

			self.current_song = self.songs.popleft()

			proc = None
			download = False

			if self.current_song.id is None:
				log.info("music - streaming audio")
				self.voice_client.play(discord.PCMVolumeTransformer(
					discord.FFmpegPCMAudio(self.current_song.url, options='-loglevel warning'), volume=0.3),
					after=self.play_next)
			elif not "music" in os.listdir('{}/../sounds'.format(os.path.dirname(__file__))) or not any(
					f.startswith("{}_".format(self.current_song.id)) for f in
					os.listdir('{}/../sounds/music'.format(os.path.dirname(__file__)))):
				if config.config["music"]["download_audio"].lower() == "true":
					log.info("music - streaming and downloading audio")

					song_name = self.current_song.name.replace("\\", "_")
					song_name = song_name.replace("/", "_")

					filename = '{}/../sounds/music/{}_{}.mp3'.format(os.path.dirname(__file__), self.current_song.id,
																	 song_name)

					pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

					args = ["ffmpeg"]
					args.extend(("-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5", "-i",
								 self.current_song.url, "-f", "mp3", "-ar", "48000", "-ac", "2", filename, "-f",
								 "s16le", "-ar", "48000", "-ac", "2", "pipe:1", "-loglevel", "warning"))

					download = True

					proc = subprocess.Popen(args, stdout=subprocess.PIPE)

					self.voice_client.play(discord.PCMVolumeTransformer(discord.PCMAudio(proc.stdout), volume=0.3),
										   after=self.play_next)
					dataBase.writeVal("music/play_times", self.current_song.id, time.time())
				else:
					log.info("music - streaming audio")
					self.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.current_song.url,
																							   before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
																							   options='-loglevel warning'),
																		volume=0.3), after=self.play_next)
			else:
				log.info("music - playing stored audio")
				for f in os.listdir('{}/../sounds/music'.format(os.path.dirname(__file__))):
					if f.startswith("{}_".format(self.current_song.id)):
						break
				filename = '{}/../sounds/music/{}'.format(os.path.dirname(__file__), f)

				self.voice_client.play(
					discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filename, options='-loglevel warning'),
												 volume=0.3), after=self.play_next)
				dataBase.writeVal("music/play_times", self.current_song.id, time.time())

			await self.play_next_song.wait()

			if proc is not None:
				log.info('Preparing to terminate ffmpeg process %s.', proc.pid)
				proc.kill()
				if proc.poll() is None:
					log.info('ffmpeg process %s has not terminated. Waiting to terminate...', proc.pid)
					proc.communicate()
					log.info('ffmpeg process %s should have terminated with a return code of %s.', proc.pid,
							 proc.returncode)
					if download:
						os.remove(filename)
				else:
					log.info('ffmpeg process %s successfully terminated with return code of %s.', proc.pid,
							 proc.returncode)


class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.voice_states = {}
		self.cleanup_task = self.bot.loop.create_task(self.cleanup_task())
		self.ytplaylist_pattern = re.compile(
			r"^((http(s?):\/\/)?www\.)?youtu(be)?((\.[a-z]{2,3}){1,2})\/watch\?(([a-zA-Z0-9]+=[a-zA-Z0-9]+)\&)*(list=[^&]*)(\&([a-zA-Z0-9]+=[a-zA-Z0-9]+))*$")
		self.link_pattern = re.compile(
			r"(https?:\/\/)?(www\.)?(([-a-zA-Z0-9@:%_\+~#=]+\.)+)([a-z]{2,})(:[1-9]+[0-9]*)?(\/[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)?")

		# fetch config from database
		for g in bot.guilds:
			getConfig(g.id)

	async def cleanup_task(self):
		log.info("starting cleanup_task")
		while True:
			play_times = dataBase.dump("music/play_times")
			# print(play_times)
			# print(time.time())

			for song_id in play_times.keys():
				last_play_time = play_times[song_id]
				# print(song_id)
				# print(last_play_time)
				if (time.time() - 604800) > last_play_time:
					try:
						for f in os.listdir('{}/../sounds/music'.format(os.path.dirname(__file__))):
							if f.startswith("{}_".format(song_id)):
								break
						filename = '{}/../sounds/music/{}'.format(os.path.dirname(__file__), f)

						os.remove(filename)
						dataBase.deleteVal("music/play_times", song_id)
						log.info("music.cleanup_task - deleted file (song_id: {}): {}".format(song_id, filename))
					except Exception as e:
						log.warning(
							"music.cleanup_task - cannot delete file (song_id: {}): {}: {}".format(song_id, filename,
																								   str(e)))

			# print("sleep")
			await asyncio.sleep(3600)

	def get_voice_state(self, server):
		state = self.voice_states.get(server.id)
		if state is None:
			state = VoiceState(self.bot)
			self.voice_states[server.id] = state
		return state

	# pause all streams
	#	async def on_disconnect():
	#		log.info("disconnected: pausing all streams")
	#		for voice_state in self.voice_states:
	#			try:
	#				await voice_state.voice_client.pause()
	#			except:
	#				pass

	# reconnect and resume all streams
	@commands.Cog.listener()
	async def on_ready(self):
		log.info("(re)connected: reconnecting to voice channels")
		for server_id in self.voice_states.keys():
			voice_state = self.voice_states[server_id]
			try:
				await voice_state.voice_client.disconnect()
			except Exception as e:
				try:
					ch_name = str(voice_state.voice_channel)
				except:
					ch_name = "UNKNOWN"
				log.warning("Cannot disconnect from channel {}: {}".format(ch_name, str(e)))
			try:
				if voice_state.voice_channel:
					voice_state.voice_client = await voice_state.voice_channel.connect()
			except Exception as e:
				try:
					ch_name = str(voice_state.voice_channel)
				except:
					ch_name = "UNKNOWN"
				log.warning("Cannot reconnect to channel {}: {}".format(ch_name, str(e)))

	@commands.command(no_pm=True, aliases=["summon"])
	async def join(self, ctx, *, channel: discord.VoiceChannel = None):
		if channel is None:
			if ctx.message.author.voice is None:
				return
			else:
				channel = ctx.message.author.voice.channel

		state = self.get_voice_state(ctx.message.guild)
		try:
			state.voice_client = await channel.connect()
			state.voice_channel = channel
		except discord.InvalidArgument:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_no_channel'])
		except discord.ClientException:
			move = False
			for ch in ctx.guild.voice_channels:
				if ctx.bot.user in ch.members and len(ch.members) == 1:
					move = True

			if channel == state.voice_channel:
				move = True

			if move == True:
				try:
					await state.voice_client.move_to(channel)
					state.voice_channel = channel
				except Exception as e:
					log.error(str(e))
					await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_channel'])
			else:
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_channel'])
		else:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_success'].format(channel.name))

	async def _playsong(self, ctx, song_name):
		if not self.link_pattern.match(song_name):
			song_name = song_name.replace(":", "")

		voice_state = self.get_voice_state(ctx.message.guild)

		ytdl_opts = {
			'format': 'webm[abr>0]/bestaudio/best',
			'prefer_ffmpeg': True,
			'default_search': 'ytsearch',
			'noplaylist': True,
			# 'quiet': True,
			'ignoreerrors': True,
			'mark-watched': True,
			'logger': log
		}

		ytdl = youtube_dl.YoutubeDL(ytdl_opts)
		info = await self.bot.loop.run_in_executor(None, ytdl.extract_info, song_name, False)

		if info is None:
			return None

		if "entries" in info:
			info = info['entries'][0]

		if info is None:
			return None

		try:
			url = info['url']

			is_twitch = 'extractor' in info and info['extractor'] == 'twitch:stream'
			if is_twitch:
				song_name = info.get('description', None)
			else:
				song_name = info.get('title', None)

			thumbnail_url = info.get('thumbnail', None)
			uploader = info.get('uploader', None)
			is_live = info.get('is_live', False)
			duration = info.get('duration', 0)

			if is_live is not True and duration < 600:
				video_id = info.get('id', None)
			else:
				video_id = None

			entry = VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url, uploader,
							   video_id)

			if getQueueMode(ctx.guild.id) == 'random' and len(voice_state.songs) > 1:
				voice_state.songs.insert(random.randint(0, len(voice_state.songs) - 1), entry)
			else:
				voice_state.songs.append(entry)
		except:
			return None

		return entry

	async def _playytlist(self, ctx, playlist_link):
		locale = config.getLocale(ctx.guild.id)

		voice_state = self.get_voice_state(ctx.message.guild)

		if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
			await ctx.send(config.strings[locale]['music']['queue_full'])
			return

		queue_mode = getQueueMode(ctx.guild.id)
		if queue_mode == 'random':
			_random = True
		else:
			_random = False

		ytdl_opts = {
			'format': 'webm[abr>0]/bestaudio/best',
			'prefer_ffmpeg': True,
			'default_search': 'ytsearch',
			'yesplaylist': True,
			'quiet': True,
			'playlistrandom': _random,
			'ignoreerrors': True,
			'mark-watched': True,
			'logger': log
		}

		await ctx.send(config.strings[locale]['music']['playytlist_warning'])

		ytdl = youtube_dl.YoutubeDL(ytdl_opts)
		info = await self.bot.loop.run_in_executor(None, ytdl.extract_info, playlist_link, False)

		locale = config.getLocale(ctx.guild.id)

		if (info['_type'] == 'playlist') and ('title' in info):
			playlist_uploader = info.get("uploader", "Unknown")

			embed = discord.Embed(title=config.strings[locale]['music']['playytlist_enqueue'].format(info['title']),
								  description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'],
															 playlist_uploader))

			if 'thumbnail' in info:
				embed.set_thumbnail(url=info['thumbnail'])

			await ctx.send(embed=embed)

			for entry in list(info['entries']):
				try:
					url = entry['url']

					is_twitch = 'extractor' in info and info['extractor'] == 'twitch:stream'
					if is_twitch:
						song_name = entry.get('description', None)
					else:
						song_name = entry.get('title', None)

					thumbnail_url = entry.get('thumbnail', None)
					uploader = entry.get('uploader', None)
					is_live = entry.get('is_live', False)
					duration = entry.get('duration', 0)

					if is_live is not True and duration < 600:
						video_id = entry.get('id', None)
					else:
						video_id = None

					if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
						await ctx.send(config.strings[locale]['music']['queue_full'])
						return

					song_entry = VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url,
											uploader, video_id)

					if queue_mode == 'random' and len(voice_state.songs) > 1:
						voice_state.songs.insert(random.randint(0, len(voice_state.songs) - 1), song_entry)
					else:
						voice_state.songs.append(song_entry)

				except Exception as error:
					log.debug('playytlist: skipping unavailable song: {}'.format(str(error)))
					continue
		else:
			await ctx.send(config.strings[locale]['music']['playytlist_no_playlist'])

	@commands.command(no_pm=True)
	async def play(self, ctx, *, name: str = None):
		if name is None:
			return None

		voice_state = self.get_voice_state(ctx.message.guild)

		if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_full'])
			return None

		locale = config.getLocale(ctx.guild.id)

		if self.ytplaylist_pattern.match(name):
			log.debug("music - playing a playlist")
			await self._playytlist(ctx, name)
		else:
			log.debug("music - playing a single video/song")
			tmp = await self._playsong(ctx, name)

			embed = discord.Embed(title=config.strings[locale]['music']['enqueued_song'].format(tmp.name),
								  description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'],
															 tmp.uploader))
			if tmp.thumbnail_url is not None:
				embed.set_thumbnail(url=tmp.thumbnail_url)

			await ctx.send(embed=embed)

	@commands.command(no_pm=True)
	async def playlist(self, ctx, *song_names: str):
		locale = config.getLocale(ctx.guild.id)

		embed = discord.Embed(title=config.strings[locale]['music']['enqueued_songs'])
		i = 0
		for name in song_names:
			tmp = await self._playsong(ctx, name)
			if tmp is not None:
				if i < 10:
					embed.add_field(name=tmp.name,
									value='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'],
														 tmp.uploader), inline=False)

				i = i + 1

		if i > 10:
			embed.set_footer(text=config.strings[locale]['music']['queue_elements_not_shown'].format(i - 10))

		await ctx.send(embed=embed)

	@commands.command(no_pm=True, aliases=["quit", "leave"])
	async def stop(self, ctx):
		state = self.get_voice_state(ctx.message.guild)
		if state.voice_client and (
				(ctx.author.voice is not None and state.voice_channel == ctx.author.voice.channel) or (
				len(discord.utils.get(ctx.guild.voice_channels, id=state.voice_channel.id).members) == 1)):
			await state.stop()

	@commands.command(no_pm=True)
	async def skip(self, ctx):
		state = self.get_voice_state(ctx.message.guild)
		if state.voice_client and ctx.author.voice is not None and state.voice_channel == ctx.author.voice.channel:
			state.skip()

	@commands.command(no_pm=True)
	async def pause(self, ctx):
		state = self.get_voice_state(ctx.message.guild)
		if state.voice_client and ctx.author.voice is not None and state.voice_channel == ctx.author.voice.channel:
			state.pause()

	@commands.command(no_pm=True, aliases=["continue", "unpause"])
	async def resume(self, ctx):
		state = self.get_voice_state(ctx.message.guild)
		if state.voice_client and ctx.author.voice is not None and state.voice_channel == ctx.author.voice.channel:
			state.resume()

	@commands.command(no_pm=True, aliases=['np', 'current'])
	async def nowplaying(self, ctx):
		voice_state = self.get_voice_state(ctx.message.guild)
		locale = config.getLocale(ctx.guild.id)

		if voice_state.current_song is None:
			embed = discord.Embed(title=config.strings[locale]['music']['nowplaying_nothing'])
			await ctx.send(embed=embed)
		else:
			embed = discord.Embed(title=config.strings[locale]['music']['nowplaying_song'])
			embed.add_field(name=config.strings[locale]['music']['nowplaying_title'],
							value=voice_state.current_song.name)
			embed.add_field(name=config.strings[locale]['music']['nowplaying_uploader'],
							value=voice_state.current_song.uploader)
			if voice_state.current_song.thumbnail_url is not None:
				embed.set_thumbnail(url=voice_state.current_song.thumbnail_url)
			await ctx.send(embed=embed)

	@commands.command(no_pm=True)
	async def loop(self, ctx, mode: str = None):
		if mode:
			mode = mode.lower()

		if mode == 'on':
			setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), mode)
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_on'])
		elif mode == 'off':
			setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), mode)
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_off'])
		elif mode is None:
			if getLoopMode(ctx.guild.id) == "on":
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_on'])
			else:
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_off'])

	@commands.command(no_pm=True)
	async def queue_mode(self, ctx, mode: str = None):
		if mode:
			mode = mode.lower()

		if mode == 'normal':
			setConfig(ctx.guild.id, mode, getLoopMode(ctx.guild.id))
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_normal'])
		elif mode == 'random':
			setConfig(ctx.guild.id, mode, getLoopMode(ctx.guild.id))
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_random'])
		elif mode is None:
			if getQueueMode(ctx.guild.id) == 'normal':
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_normal'])
			else:
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_random'])

	@commands.command(no_pm=True)
	async def repeat(self, ctx):
		voice_state = self.get_voice_state(ctx.message.guild)

		if ctx.author.voice is None or voice_state.voice_channel != ctx.author.voice.channel:
			return

		previous = voice_state.previous_song
		current = voice_state.current_song
		if previous is not None:
			loop = getLoopMode(ctx.guild.id)
			if loop == "on":
				setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), "off")

				if len(voice_state.songs) > 0 and voice_state.songs[len(voice_state.songs) - 1] == previous:
					voice_state.songs.pop()

			if current:
				voice_state.songs.appendleft(current)
			voice_state.songs.appendleft(previous)

			if voice_state.is_playing():
				voice_state.skip()

			if loop == "on":
				setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), "on")

			locale = config.getLocale(ctx.guild.id)

			embed = discord.Embed(title=config.strings[locale]['music']['repeat_song'].format(previous.name),
								  description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'],
															 previous.uploader))
			if previous.thumbnail_url is not None:
				embed.set_thumbnail(url=previous.thumbnail_url)

			await ctx.send(embed=embed)

	@commands.command(no_pm=True)
	async def queue(self, ctx):
		voice_state = self.get_voice_state(ctx.message.guild)
		songs = asyncio.Queue()

		for t in voice_state.songs:
			await songs.put(t)

		locale = config.getLocale(ctx.guild.id)

		if songs.empty():
			embed = discord.Embed(title=config.strings[locale]['music']['queue_title'],
								  description=config.strings[locale]['music']['queue_empty'])
		else:
			embed = discord.Embed(title=config.strings[locale]['music']['queue_title'])
			for i in range(1, 11):
				song = await songs.get()
				embed.add_field(name='{}: {}'.format(i, song.name),
								value='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'],
													 song.uploader), inline=False)
				if songs.empty():
					break
			if songs.qsize() > 0:
				embed.set_footer(text=config.strings[locale]['music']['queue_elements_not_shown'].format(songs.qsize()))

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Music(bot))
	log.info("Youtube-dl version: " + str(youtube_dl.version.__version__))
