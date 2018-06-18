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

import youtube_dl
import asyncio
import time
import os
import subprocess
import shlex
import collections
import random
import psycopg2
from psycopg2 import sql

import config
from logger import logger as log

if not discord.opus.is_loaded():
	try:
		discord.opus.load_opus('opus')
	except:
		try:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so')
		except:
			discord.opus.load_opus('.apt/usr/lib/x86_64-linux-gnu/libopus.so.0')
		
_config={}

def getConfig(id):
	if str(id) in _config.keys():
		return [id, _config[str(id)]["queue_mode"], _config[str(id)]["loop"]]

	try:
		conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
		cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
		cur.execute(sql.SQL("SELECT * FROM music_config WHERE id = %s"), [str(id)])

		ret = None
		for row in cur:
			if row[0] == str(id):
				ret = row
				_config[str(id)]={
					"queue_mode" : ret[1],
					"loop" : ret[2]
					}

		cur.close()
		conn.close()

		return ret
	except Exception as e:
		log.warning("music - cannot read from database: %s", str(e))
		return None

def setConfig(id, queue_mode, loop):
	try:
		conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
		cur=conn.cursor()

		old = getConfig(id)
		if old == None:
			cur.execute(sql.SQL("INSERT INTO music_config VALUES (%s, %s, %s)"), [str(id), queue_mode, loop])
		else:
			cur.execute(sql.SQL("UPDATE music_config SET id = %s, queue_mode = %s, loop = %s WHERE id = %s"), [str(id), queue_mode, loop, str(id)])	
	
		conn.commit()

		cur.close()
		conn.close()
	except Exception as e:
		log.warning("music - cannot write to database: %s", str(e))

	_config[str(id)]={
		"queue_mode" : queue_mode,
		"loop" : loop
		}

def getQueueMode(id):
	try:
		data=getConfig(id)
	except:
		return "normal"

	if data != None:
		return data[1]

	return "normal"

def getLoopMode(id):
	try:
		data=getConfig(id)
	except:
		return "off"

	if data != None:
		return data[2]

	return "off"

class VoiceEntry:
	def __init__(self, requester, channel, song_name, url, thumbnail_url, uploader):
		self.requester=requester
		self.channel=channel
		self.name=song_name
		self.url=url
		self.thumbnail_url=thumbnail_url
		self.uploader=uploader

class VoiceState:
	def __init__(self, bot):
		self.bot=bot
		self.current_song=None
		self.previous_song=None
		self.voice_client=None
		self.voice_channel=None
		#self.loop=False
		#self.queue_mode="normal"
		#self.songs=asyncio.Queue(maxsize=1000)
		self.songs=collections.deque(maxlen=1000)
		self.play_next_song=asyncio.Event()
		self.audio_player=self.bot.loop.create_task(self.audio_player_task())

	def skip(self):
		self.voice_client.stop()

	async def stop(self):
		#while self.songs.empty() == False:
		#	await self.songs.get()
		if len(self.songs) > 0:
			self.songs.clear()
		await self.voice_client.disconnect()
		self.voice_channel=None
		self.current_song=None
		self.previous_song=None

	def pause(self):
		self.voice_client.pause()

	def resume(self):
		self.voice_client.resume()

	def play_next(self, error):
		self.previous_song=self.current_song
		self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

	async def audio_player_task(self):
		while True:
			self.play_next_song.clear()

			wait=True
			while wait:
				if self.voice_client is not None:
					if self.voice_client.is_connected():
						wait=False
				await asyncio.sleep(1.0)

			if getLoopMode(self.voice_channel.guild.id) == "on" and self.previous_song != None:
				#await self.songs.put(self.previous_song)
				self.songs.append(self.previous_song)

			while len(self.songs) == 0:
				await asyncio.sleep(1.0)

			#self.current_song=await self.songs.get()
			self.current_song=self.songs.popleft()

			self.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.current_song.url, options='-loglevel warning'), volume=0.3), after=self.play_next)
			await self.play_next_song.wait()

class Music:
	def __init__(self, bot):
		self.bot=bot
		self.voice_states={}

		#fetch config from database
		for g in bot.guilds:
			getConfig(g.id)

	def get_voice_state(self, server):
		state=self.voice_states.get(server.id)
		if state is None:
			state=VoiceState(self.bot)
			self.voice_states[server.id]=state
		return state

	#pause all streams
	async def on_disconnect():
		log.info("disconnected: pausing all streams")
		for voice_state in self.voice_states:
			try:
#				voice_state.pause()
				await voice_state.voice_client.disconnect()
			except:
				pass

	#reconnect and resume all streams
	async def on_connect(self):
		log.info("(re)connected: reconnecting to voice channels")
		for voice_state in self.voice_states:
#			try:
#				if voice_state.voice_client.is_connected():
#					await voice_state.voice_client.disconnect()
#			except:
#				pass
			try:
				if voice_state.voice_channel:
					voice_state.voice_client=await voice_state.voice_channel.connect()
#					voice_state.resume()
			except:
				pass

	@commands.command(pass_context=True, no_pm=True, aliases=["summon"])
	async def join(self, ctx, *, channel : discord.VoiceChannel=None):
		if channel == None:
			if ctx.message.author.voice.channel == None:
				return
			else:
				channel=ctx.message.author.voice.channel

		state=self.get_voice_state(ctx.message.guild)
		try:
			state.voice_client=await channel.connect()
			state.voice_channel=channel
		except discord.ClientException:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_channel'])
		except discord.InvalidArgument:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_no_channel'])
		else:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['join_success'].format(channel.name))

	async def play(self, ctx, song_name):
		voice_state=self.get_voice_state(ctx.message.guild)

		if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_full'])
			return None

		if song_name.startswith("http://") == False and song_name.startswith("https://") == False:
			song_name=song_name.replace(":", "")

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
		info=await self.bot.loop.run_in_executor(None, ytdl.extract_info, song_name, False)
		if "entries" in info:
			info=info['entries'][0]

		url=info['url']

		is_twitch='twitch' in url
		if is_twitch:
			song_name=info['description']
		else:
			song_name=info['title']

		if 'thumbnail' in info:
			thumbnail_url=info['thumbnail']
		else:
			thumbnail_url=None

		if 'uploader' in info:
			uploader=info['uploader']
		else:
			uploader='Unknown'

		entry=VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url, uploader)

		if getQueueMode(ctx.guild.id) == 'random' and len(voice_state.songs) > 1:
			voice_state.songs.insert(random.randint(0, len(voice_state.songs)-1), entry)
		else:
			voice_state.songs.append(entry)

		return entry

	@commands.command(pass_context=True, no_pm=True)
	async def playlist(self, ctx, *song_names : str):
		locale=config.getLocale(ctx.guild.id)

		embed=discord.Embed(title=config.strings[locale]['music']['enqueued_songs'])
		i=0
		for name in song_names:
			tmp=await self.play(ctx, name)
			if tmp == None:
				break

			if i < 10:
				embed.add_field(name=tmp.name, value='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'], tmp.uploader), inline=False)

			i=i+1

		if i > 10:
			embed.set_footer(text=config.strings[locale]['music']['queue_elements_not_shown'].format(i - 10))

		await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	async def playsong(self, ctx, *, song_name : str):
		tmp=await self.play(ctx, song_name)
		if tmp == None:
			return

		locale=config.getLocale(ctx.guild.id)
		embed=discord.Embed(title=config.strings[locale]['music']['enqueued_song'].format(tmp.name), description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'], tmp.uploader))
		if tmp.thumbnail_url != None:
			embed.set_thumbnail(url=tmp.thumbnail_url)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)#, description=config.strings[config.getLocale(ctx.guild.id)]['music']['playytlist_description'])
	async def playytlist(self, ctx, *, playlist_link : str):
		locale=config.getLocale(ctx.guild.id)

		voice_state=self.get_voice_state(ctx.message.guild)

		if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
			await ctx.send(config.strings[locale]['music']['queue_full'])
			return

		queue_mode=getQueueMode(ctx.guild.id)
		if queue_mode == 'random':
			_random=True
		else:
			_random=False

		ytdl_opts={
			'format': 'webm[abr>0]/bestaudio/best',
			'prefer_ffmpeg': True,
			'default_search': 'ytsearch',
			'yesplaylist': True,
			'quiet': True,
			'playlistrandom' : _random,
			'ignoreerrors' : True,
			'logger' : log
		}

		await ctx.send(config.strings[locale]['music']['playytlist_warning'])

		ytdl=youtube_dl.YoutubeDL(ytdl_opts)
		info=await self.bot.loop.run_in_executor(None, ytdl.extract_info, playlist_link, False)

		locale=config.getLocale(ctx.guild.id)

		if (info['_type'] == 'playlist') and ('title' in info):
			if "uploader" in info:
				playlist_uploader=info["uploader"]
			else:
				playlist_uploader="Unknown"

			embed=discord.Embed(title=config.strings[locale]['music']['playytlist_enqueue'].format(info['title']), description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'], playlist_uploader))

			if 'thumbnail' in info:
				embed.set_thumbnail(url=info['thumbnail'])

			await ctx.send(embed=embed)

			for entry in list(info['entries']):
				try:
					url=entry['url']
				except:
					log.debug('playytlist: skipping unavailable song')
					continue

				is_twitch='twitch' in url
				if is_twitch:
					song_name=entry['description']
				else:
					song_name=entry['title']

				if 'thumbnail' in entry:
					thumbnail_url=entry['thumbnail']
				else:
					thumbnail_url=None

				if 'uploader' in entry:
					uploader=entry['uploader']
				else:
					uploader=None

				if voice_state.songs.maxlen and len(voice_state.songs) == voice_state.songs.maxlen:
					await ctx.send(config.strings[locale]['music']['queue_full'])
					return

				song_entry=VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url, uploader)

				if queue_mode == 'random' and len(voice_state.songs) > 1:
					voice_state.songs.insert(random.randint(0, len(voice_state.songs)-1), song_entry)
				else:
					voice_state.songs.append(song_entry)
		else:
			await ctx.send(config.strings[locale]['music']['playytlist_no_playlist'])

	@commands.command(pass_context=True, no_pm=True, aliases=["quit"])
	async def stop(self, ctx):
		state=self.get_voice_state(ctx.message.guild)
		if state.voice_client:
			await state.stop()

	@commands.command(pass_context=True, no_pm=True)
	async def skip(self, ctx):
		state=self.get_voice_state(ctx.message.guild)
		if state.voice_client:
			state.skip()

	@commands.command(pass_context=True, no_pm=True)
	async def pause(self, ctx):
		state=self.get_voice_state(ctx.message.guild)
		if state.voice_client:
			state.pause()

	@commands.command(pass_context=True, no_pm=True, aliases=["continue"])
	async def resume(self, ctx):
		state=self.get_voice_state(ctx.message.guild)
		if state.voice_client:
			state.resume()

	@commands.command(pass_context=True, no_pm=True, aliases=['np', 'current'])
	async def nowplaying(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)
		locale=config.getLocale(ctx.guild.id)

		if voice_state.current_song == None:
			embed=discord.Embed(title=config.strings[locale]['music']['nowplaying_nothing'])
			await ctx.send(embed=embed)
		else:
			embed=discord.Embed(title=config.strings[locale]['music']['nowplaying_song'])
			embed.add_field(name=config.strings[locale]['music']['nowplaying_title'], value=voice_state.current_song.name)
			embed.add_field(name=config.strings[locale]['music']['nowplaying_uploader'], value=voice_state.current_song.uploader)
			embed.add_field(name=config.strings[locale]['music']['nowplaying_requester'], value=voice_state.current_song.requester.display_name)
			if voice_state.current_song.thumbnail_url != None:
				embed.set_thumbnail(url=voice_state.current_song.thumbnail_url)
			await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	async def loop(self, ctx, mode : str=None):
		if mode:
			mode=mode.lower()

		if mode == 'on':
			setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), mode)
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_on'])
		elif mode == 'off':
			setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), mode)
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_off'])
		elif mode == None:
			if getLoopMode(ctx.guild.id) == "on":
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_on'])
			else:
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['loop_off'])

	@commands.command(pass_context=True, no_pm=True)
	async def queue_mode(self, ctx, mode : str=None):
		if mode:
			mode=mode.lower()

		if mode == 'normal':
			setConfig(ctx.guild.id, mode, getLoopMode(ctx.guild.id))
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_normal'])
		elif mode == 'random':
			setConfig(ctx.guild.id, mode, getLoopMode(ctx.guild.id))
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_random'])
		elif mode == None:
			if getQueueMode(ctx.guild.id) == 'normal':
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_normal'])
			else:
				await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['music']['queue_mode_random'])

	@commands.command(pass_context=True, no_pm=True)
	async def repeat(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)

		previous=voice_state.previous_song
		current=voice_state.current_song
		if previous is not None:
			loop=getLoopMode(ctx.guild.id)
			if loop == "on":
				setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), "off")

				if len(voice_state.songs) > 0 and voice_state.songs[len(voice_state.songs)-1] == previous:
					voice_state.songs.pop()

			if current:
				voice_state.songs.appendleft(current)
			voice_state.songs.appendleft(previous)

			voice_state.skip()

			while current == voice_state.current_song:
				await asyncio.sleep(0.1)

			if loop == "on":
				setConfig(ctx.guild.id, getQueueMode(ctx.guild.id), "on")

			locale=config.getLocale(ctx.guild.id)

			embed=discord.Embed(title=config.strings[locale]['music']['repeat_song'].format(previous.name), description='{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'], previous.uploader))
			if previous.thumbnail_url != None:
				embed.set_thumbnail(url=previous.thumbnail_url)

			await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	async def queue(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)
		songs=asyncio.Queue()

		for t in voice_state.songs:
			await songs.put(t)

		locale=config.getLocale(ctx.guild.id)

		if songs.empty():
			embed=discord.Embed(title=config.strings[locale]['music']['queue_title'], description=config.strings[locale]['music']['queue_empty'])
		else:
			embed=discord.Embed(title=config.strings[locale]['music']['queue_title'])
			for i in range(1, 11):
				song=await songs.get()
				embed.add_field(name='{}: {}'.format(i, song.name), value='{} {}\n{} {}'.format(config.strings[locale]['music']['nowplaying_uploader'], song.uploader, config.strings[locale]['music']['nowplaying_requester'], song.requester.display_name), inline=False)
				if songs.empty():
					break
			if songs.qsize() > 0:
				embed.set_footer(text=config.strings[locale]['music']['queue_elements_not_shown'].format(songs.qsize()))

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Music(bot))
	log.info("Youtube-dl version: " + str(youtube_dl.version.__version__))
