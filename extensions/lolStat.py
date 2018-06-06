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
	def __init__(self):
		self.retry_after={
				"static-data" : time.time(),
				"summoner" : time.time(),
				"league" : time.time(),
				"match" : time.time(),
				"champion" : time.time(),
				"champion-mastery" : time.time(),
				"other" : time.time()
			}
		self.refresh_interval={
				"static-data" : 14400,
				"summoner" : 60,
				"league" : 300,
				"match" : 120,
				"champion" : 600,
				"champion-mastery" : 600,
				"other" : 30
			}

		try:
			keyFile=open("riotKey.txt", "r")
			self.key=keyFile.readline()[:-1]
			keyFile.close()
		except:
			self.key=os.getenv("RIOT_KEY")

			if self.key == None:
				log.error("No Riot Key found. Please save a riotKey.txt or specify a environment variable 'RIOT_KEY'.")

		self.allowed_locales=self.getData("lol/static-data/v3/languages")["data"]

	def getData(self, name):
		endpoint="other"

		if name.startswith("lol/static-data"):
			endpoint="static-data"
		elif name.startswith("lol/champion-mastery"):
			endpoint="champion-mastery"
		elif name.startswith("lol/platform/v3/champions"):
			endpoint="champion"
		elif name.startswith("lol/league"):
			endpoint="league"
		elif name.startswith("lol/match"):
			endpoint="match"
		elif name.startswith("lol/summoner"):
			endpoint="summoner"

		fetchtime=dataBase.readVal('lolStat/' + name.lower(), 'fetchtime')
		if (fetchtime > 0) and (fetchtime+self.refresh_interval[endpoint] > time.time()):
#			print('lolStat/' + name + '.json')
			data=dataBase.dump('lolStat/' + name.lower())
			if data == {}:
				return None
			return data

		elif self.retry_after[endpoint] > time.time():
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
			except urllib.error.HTTPError as e:
				if e.code == 429:
					self.retry_after[endpoint]=time.time() + int(e.headers['Retry-After'])
					log.info('lolStat.getData: got 429: rety after {} seconds. searching for cached results'.format(int(e.headers['Retry-After'])))
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

				data.update({"fetchtime" : time.time()})
				
				filename='dataBase/' + "lolStat/" + name + '.json'
				filename=filename.replace("&", "_")
				filename=filename.replace("=", "_")
				filename=filename.replace("?", "_")

				with open(filename, 'w', encoding='utf-8') as file:
					json.dump(data, file)

				return data

		return None

	@commands.command(pass_context=True, no_pm=True)
	async def getPlayerInfo(self, ctx, *, name : str):
		summoner=name
		summoner=urllib.request.quote(summoner, safe=':/')

		data=await ctx.bot.loop.run_in_executor(None, self.getData, str('lol/summoner/v3/summoners/by-name/' + summoner))
		versions=await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/v3/versions')

		locale=config.getLocale(ctx.guild.id)

		if data != None:
			level=data['summonerLevel']
			summoner=data['name']
			icon_id=data['profileIconId']
			version=versions['data'][0]

			embed=discord.Embed(title=summoner)
			embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png'.format(version, icon_id))

			embed.add_field(name=config.strings[locale]['lolStat']['playerInfo_level'], value=level)

			league=self.getData('lol/league/v3/positions/by-summoner/{}'.format(data['id']))
			if league != None:
				for l in league['data']:
					embed.add_field(name=config.strings[locale]['lolStat']['playerInfo_rank'], value='{} {}'.format(l['tier'], l['rank']))

			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

	@commands.command(pass_context=True, no_pm=True)
	async def getChampionRotation(self, ctx):
		data=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/platform/v3/champions?freeToPlay=true")

		locale=config.getLocale(ctx.guild.id)

		if locale in self.allowed_locales:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?locale={}&champListData=all&tags=all&dataById=true".format(locale))
		else:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?&champListData=all&tags=all&dataById=true")

		embed=discord.Embed(title=config.strings[locale]["lolStat"]["championRotationTitle"])

		for champion in data["champions"]:
			championData=allChampionData["data"]["{}".format(champion["id"])]

			tags=config.strings[locale]["lolStat"][championData["tags"][0]]
			for i in range(1, len(championData["tags"])):
				tags="{}, {}".format(tags, config.strings[locale]["lolStat"][championData["tags"][i]])
			
			embed.add_field(name=championData["name"], value=tags)

		await ctx.send(embed=embed)

	@commands.command(pass_context=True, no_pm=True)
	async def getChampionLore(self, ctx, *, championName : str):
		locale=config.getLocale(ctx.guild.id)

		if locale in self.allowed_locales:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?locale={}&champListData=all&tags=all&dataById=true".format(locale))
		else:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?&champListData=all&tags=all&dataById=true")

		if allChampionData != None:
			version=allChampionData["version"]

			for championKey in allChampionData["keys"]:
				championData=allChampionData["data"][str(championKey)]
				if championData["name"].lower() == championName.lower():
					embed=discord.Embed(title=championData["name"])
					embed.add_field(name=championData["title"], value=championData["lore"])
					embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/{}/{}'.format(version, championData["image"]["group"], championData["image"]["full"]))
					await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

	@commands.command(pass_context=True, no_pm=True)
	async def getChampionStats(self, ctx, *, championName : str):
		locale=config.getLocale(ctx.guild.id)

		if locale in self.allowed_locales:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?locale={}&champListData=all&tags=all&dataById=true".format(locale))
		else:
			allChampionData=await ctx.bot.loop.run_in_executor(None, self.getData, "lol/static-data/v3/champions?&champListData=all&tags=all&dataById=true")

		if allChampionData != None:
			version=allChampionData["version"]

			for championKey in allChampionData["keys"]:
				championData=allChampionData["data"][str(championKey)]
				if championData["name"].lower() == championName.lower():
					embed=discord.Embed(title=championData["name"])
					embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/{}/{}'.format(version, championData["image"]["group"], championData["image"]["full"]))

					for stat_name, stat_value in championData["stats"].items():
						if stat_value > 0:
							try:
								name=config.strings[locale]["lolStat"][str(stat_name)]
							except:
								name=str(stat_name)

							embed.add_field(name=name, value=stat_value)

					for spell in championData["spells"]:
						spellText=spell["sanitizedTooltip"]

						if "effectBurn" in spell:
							for i in range(1, len(spell["effectBurn"])):
								spellText=spellText.replace("{{ e" + str(i) + " }}", spell["effectBurn"][i])

						if "vars" in spell:
							for var in spell["vars"]:
								var_text=str(int(round(var["coeff"][0]*100, 3)))
								for j in range(1, len(var["coeff"])):
									var_text=var_text + "/" + str(int(round(var["coeff"][j]*100, 3)))

								try:
									link=config.strings[locale]["lolStat"][str(var["link"])]
								except:
									link=str(var["link"])
								var_text=var_text + "% " + link
								spellText=spellText.replace("{{ " + var["key"] + " }}", var_text)

						embed.add_field(name=spell["name"], value=spellText, inline=False)

					embed.set_footer(text=config.strings[locale]["lolStat"]["champion_data_disclaimer"])
					await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

def setup(bot):
	bot.add_cog(LeagueOfLegends())
