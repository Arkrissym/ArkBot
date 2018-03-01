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

import config
from logger import logger as log

if not discord.opus.is_loaded():
	discord.opus.load_opus('opus')

class myFFmpegPCMAudio(discord.AudioSource):
	def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
		stdin = None if not pipe else source

		args = [executable]

		if isinstance(before_options, str):
			args.extend(shlex.split(before_options))

		lsource=str('/tmp/music_cache_' + str(time.time()) + '.wav')
		os.system('mkfifo ' + lsource)
		self.fifo_file=lsource

		args.extend(('-re', '-i'))
		args.append(lsource)
		args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'error', '-bufsize', '512000k'))

		if isinstance(options, str):
			args.extend(shlex.split(options))

		#added a buffer (better for livestreams)
		args.append('pipe:1')

		args2=executable
		args2=args2 + str(' -i ')
		args2=args2 + str('-' if pipe else str('\"' + source + '\"'))
		args2=args2 + str(' -loglevel error -f wav -ar 48000 -ac 2 -vn')
		args2=args2 + str(' pipe:1 | mbuffer -Q -q -v 0 -c -m 2048k > ' + lsource)

		self._process = None
		self._process2=None
		try:
			self._process2=subprocess.Popen(args2, stdin=stdin, shell=True)
		except FileNotFoundError:
			raise discord.ClientException(executable + ' was not found.') from None
		except subprocess.SubprocessError as e:
			raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(e)) from e

		try:
			self._process = subprocess.Popen(args, stdin=stdin, stdout=subprocess.PIPE, stderr=stderr)
			self._stdout = self._process.stdout
		except FileNotFoundError:
			raise discord.ClientException(executable + ' was not found.') from None
		except subprocess.SubprocessError as e:
			raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(e)) from e

	def read(self):
		ret = self._stdout.read(discord.opus.Encoder.FRAME_SIZE)
		if len(ret) != discord.opus.Encoder.FRAME_SIZE:
			return b''
		return ret

	def cleanup(self):
		proc = self._process2
		if proc is not None:
			proc.kill()
			log.debug('Preparing to terminate ffmpeg process %s.', proc.pid)
			proc.kill()
			if proc.poll() is None:
				log.info('ffmpeg process %s has not terminated. Waiting to terminate...', proc.pid)
				proc.communicate()
				log.info('ffmpeg process %s should have terminated with a return code of %s.', proc.pid, proc.returncode)
			else:
				log.info('ffmpeg process %s successfully terminated with return code of %s.', proc.pid, proc.returncode)
		self._process2=None

		proc = self._process
		if proc is not None:
			log.debug('Preparing to terminate ffmpeg process %s.', proc.pid)
			proc.kill()
			if proc.poll() is None:
				log.info('ffmpeg process %s has not terminated. Waiting to terminate...', proc.pid)
				proc.communicate()
				log.info('ffmpeg process %s should have terminated with a return code of %s.', proc.pid, proc.returncode)
			else:
				log.info('ffmpeg process %s successfully terminated with return code of %s.', proc.pid, proc.returncode)
		self._process = None

		os.system('rm -f ' + self.fifo_file)

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
		self.songs=asyncio.Queue(maxsize=1000)
		self.play_next_song=asyncio.Event()
		self.audio_player=self.bot.loop.create_task(self.audio_player_task())

	def skip(self):
		self.voice_client.stop()

	async def stop(self):
		while self.songs.empty() == False:
			await self.songs.get()
		await self.voice_client.disconnect()
		self.voice_channel=None
		self.current_song=None

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
			self.current_song=None
			wait=True
			while wait:
				if self.voice_client is not None:
					if self.voice_client.is_connected():
						wait=False
				await asyncio.sleep(1.0)
			self.current_song=await self.songs.get()
			self.voice_client.play(discord.PCMVolumeTransformer(myFFmpegPCMAudio(self.current_song.url), volume=0.1), after=self.play_next)
			await self.play_next_song.wait()

class Music:
	def __init__(self, bot):
		self.bot=bot
		self.voice_states={}

	def get_voice_state(self, server):
		state=self.voice_states.get(server.id)
		if state is None:
			state=VoiceState(self.bot)
			self.voice_states[server.id]=state
		return state

	@commands.command(pass_context=True, no_pm=True)
#	@commands.has_permissions(administrator=True)
	async def join(self, ctx, *, channel : discord.VoiceChannel):
		state=self.get_voice_state(ctx.message.guild)
		try:
			state.voice_client=await channel.connect()
			state.voice_channel=channel
		except discord.ClientException:
			await ctx.send(config.strings['music']['join_channel'])
		except discord.InvalidArgument:
			await ctx.send(config.strings['music']['join_no_channel'])
		else:
			await ctx.send(config.strings['music']['join_success'].format(channel.name))

	async def play(self, ctx, song_name):
		voice_state=self.get_voice_state(ctx.message.guild)

		if voice_state.songs.full():
			await ctx.send(config.strings['music']['queue_full'])
			return

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
			uploader=None

		entry=VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url, uploader)
		await voice_state.songs.put(entry)
		await ctx.send(config.strings['music']['enqueued_song'].format(song_name))

	@commands.command(pass_context=True, no_pm=True)
	async def playlist(self, ctx, *song_names : str):
		for name in song_names:
			await self.play(ctx, name)

	@commands.command(pass_context=True, no_pm=True)
	async def playsong(self, ctx, *, song_name : str):
		await self.play(ctx, song_name)

	@commands.command(pass_context=True, no_pm=True, description=config.strings['music']['playytlist_description'])
	async def playytlist(self, ctx, mode : str, *, playlist_link : str):
		voice_state=self.get_voice_state(ctx.message.guild)

		if voice_state.songs.full():
			await ctx.send(config.strings['music']['queue_full'])
			return

		if mode == 'random':
			random=True
			reverse=False
		elif mode == 'reverse':
			random=False
			reverse=True
		else:
			random=False
			reverse=False

		ytdl_opts={
			'format': 'webm[abr>0]/bestaudio/best',
			'prefer_ffmpeg': True,
			'default_search': 'ytsearch',
			'yesplaylist': True,
			'quiet': True,
			'playlistrandom' : random,
			'playlistreverse' : reverse,
			'ignoreerrors' : True,
			'logger' : log
		}

		await ctx.send(config.strings['music']['playytlist_warning'])

		ytdl=youtube_dl.YoutubeDL(ytdl_opts)
		info=await self.bot.loop.run_in_executor(None, ytdl.extract_info, playlist_link, False)

		if (info['_type'] == 'playlist') and ('title' in info):
			await ctx.send(config.strings['music']['playytlist_enqueue'].format(info['title']))
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

				if voice_state.songs.full():
					await ctx.send(config.strings['music']['queue_full'])
					return

				if 'thumbnail' in info:
					thumbnail_url=entry['thumbnail']
				else:
					thumbnail_url=None

				if 'uploader' in info:
					uploader=entry['uploader']
				else:
					uploader=None

				song_entry=VoiceEntry(ctx.message.author, ctx.message.channel, song_name, url, thumbnail_url, uploader)
				await voice_state.songs.put(song_entry)
		else:
			await ctx.send(config.strings['music']['playytlist_no_playlist'])

	@commands.command(pass_context=True, no_pm=True)
#	@commands.has_permissions(administrator=True)
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

	@commands.command(pass_context=True, no_pm=True)
	async def resume(self, ctx):
		state=self.get_voice_state(ctx.message.guild)
		if state.voice_client:
			state.resume()

	@commands.command(pass_context=True, no_pm=True, aliases=['np', 'current'])
	async def nowplaying(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)

		if voice_state.current_song == None:
			embed=discord.Embed(title=config.strings['music']['nowplaying_nothing'])
			await ctx.send(embed=embed)
		else:
			embed=discord.Embed(title=config.strings['music']['nowplaying_song'])
			embed.add_field(name=config.strings['music']['nowplaying_title'], value=voice_state.current_song.name)
			embed.add_field(name=config.strings['music']['nowplaying_uploader'], value=voice_state.current_song.uploader)
			embed.add_field(name=config.strings['music']['nowplaying_requester'], value=voice_state.current_song.requester.display_name)
			if voice_state.current_song.thumbnail_url != None:
				embed.set_thumbnail(url=voice_state.current_song.thumbnail_url)
			await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	async def repeat(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)

		previous=voice_state.previous_song
		if previous is not None:
			await voice_state.songs.put(previous)
			await ctx.send(config.strings['music']['reenqueued_song'].format(previous.name))

	@commands.command(pass_context=True, no_pm=True)
	async def queue(self, ctx):
		voice_state=self.get_voice_state(ctx.message.guild)
		songs=asyncio.Queue()
		for t in range(0, voice_state.songs.qsize()):
			tmp=await voice_state.songs.get()
			await voice_state.songs.put(tmp)
			await songs.put(tmp)

		if songs.empty():
			embed=discord.Embed(title=config.strings['music']['queue_title'], description=config.strings['music']['queue_empty'])
		else:
			embed=discord.Embed(title=config.strings['music']['queue_title'])
			for i in range(1, 11):
				song=await songs.get()
				embed.add_field(name='{}: {}'.format(i, song.name), value='{} {}\n{} {}'.format(config.strings['music']['nowplaying_uploader'], song.uploader, config.strings['music']['nowplaying_requester'], song.requester.display_name), inline=False)
				if songs.empty():
					break
			if songs.qsize() > 0:
				embed.set_footer(text=config.strings['music']['queue_elements_not_shown'].format(songs.qsize()))

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Music(bot))
