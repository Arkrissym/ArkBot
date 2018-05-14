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

import urllib.request
import urllib.error
import json
import time
import os

import dataBase
import config
from logger import logger as log

class LeagueOfLegends:
	def __init__(self, bot):
		self.bot=bot
		self.lastrun=time.time()

		try:
			keyFile=open("riotKey.txt", "r")
			self.key=keyFile.readline()[:-1]
			keyFile.close()
		except:
			self.key=os.getenv("RIOT_KEY")

			if self.key == None:
				log.error("No Riot Key found. Please save a riotKey.txt or specify a environment variable 'RIOT_KEY'.")

		self.allowed_locales=self.getData("/lol/static-data/v3/languages")["data"]
		#print(self.allowed_locales)

	def getData(self, name):
		fetchtime=dataBase.readVal('lolStat/' + name.lower(), 'fetchtime')
		if (fetchtime > 0) and (fetchtime+300 > time.time()):
#			print('lolStat/' + name + '.json')
			data=dataBase.dump('lolStat/' + name.lower())
			if data == {}:
				return None
			return data

		elif self.lastrun > time.time():
			log.info('lolStat.getData: timeout. searching for cached results')
			data=dataBase.dump('lolStat/' + name.lower())
			if data == {}:
				return None
			return data

		else:
			link='https://euw1.api.riotgames.com/' + name
			log.info('lolStat.getData: downloading {}'.format(link))
			req=urllib.request.Request(link)
			req.add_header('X-Riot-Token', self.key)
			try:
				url=urllib.request.urlopen(req)
#				self.lastrun=time.time()
			except urllib.error.HTTPError as e:
				if e.code == 429:
					self.lastrun=time.time() + int(e.headers['Retry-After'])
					log.info('lolStat.getData: got 429: timeout. searching for cached results')
					data=dataBase.dump('lolStat/' + name.lower())
					if data == {}:
						return None
					return data
				else:
					log.error('lolStat.getData: HTTPError: {}'.format(e.code))
			except urllib.error.URLError as e:
				log.error('lolStat.getData: URLError: {}'.format(e.reason))
			else:
				data = json.loads(url.read().decode())

				if isinstance(data, list):
					data={'data' : data}
				for keyName in data.keys():
					dataBase.writeVal('lolStat/' + name.lower(), keyName, data[keyName])
				dataBase.writeVal('lolStat/' + name.lower(), 'fetchtime', time.time())

				return data

		return None

	@commands.command(pass_context=True, no_pm=True)
	async def getPlayerInfo(self, ctx, name : str):
		summoner=name
		summoner=urllib.request.quote(summoner, safe=':/')

		data=self.getData('lol/summoner/v3/summoners/by-name/' + summoner)
		versions=self.getData('lol/static-data/v3/versions')

		if data != None:
			level=data['summonerLevel']
			summoner=data['name']
			icon_id=data['profileIconId']
			version=versions['data'][0]

			embed=discord.Embed(title=summoner)
			embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png'.format(version, icon_id))

			embed.add_field(name=config.strings[config.getLocale(ctx.guild.id)]['lolStat']['playerInfo_level'], value=level)

			league=self.getData('lol/league/v3/positions/by-summoner/{}'.format(data['id']))
			if league != None:
				for l in league['data']:
					embed.add_field(name=config.strings[config.getLocale(ctx.guild.id)]['lolStat']['playerInfo_rank'], value='{} {}'.format(l['tier'], l['rank']))

			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[config.getLocale(ctx.guild.id)]['lolStat']['lstatlevel_fail'])

	@commands.command(pass_context=True, no_pm=True)
	async def getChampionRotation(self, ctx):
		data=self.getData("lol/platform/v3/champions?freeToPlay=true")
		#allChampionData=self.getData("lol/static-data/v3/champions?locale={}&champListData=all&tags=all&dataById=true".format(config.config["bot"]["locale"]))
		if config.getLocale(ctx.guild.id) in self.allowed_locales:
			allChampionData=self.getData("lol/static-data/v3/champions?locale={}&champListData=all&tags=all&dataById=true".format(config.getLocale(ctx.guild.id)))
		else:
			allChampionData=self.getData("lol/static-data/v3/champions?&champListData=all&tags=all&dataById=true")

		embed=discord.Embed(title=config.strings[config.getLocale(ctx.guild.id)]["lolStat"]["championRotationTitle"])

		for champion in data["champions"]:
			championData=allChampionData["data"]["{}".format(champion["id"])]

			#print(championData["name"])
			tags=config.strings[config.getLocale(ctx.guild.id)]["lolStat"][championData["tags"][0]]
			for i in range(1, len(championData["tags"])):
				#print(config.strings["lolStat"][tag])
				tags="{}, {}".format(tags, config.strings[config.getLocale(ctx.guild.id)]["lolStat"][championData["tags"][i]])
			
			embed.add_field(name=championData["name"], value=tags)

		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(LeagueOfLegends(bot))
