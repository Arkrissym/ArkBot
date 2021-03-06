# MIT License
# see LICENSE for details

# Copyright (c) 2017-2019 Arkrissym


import json
import os
import pathlib
import re
import time
import urllib.error
import urllib.request

import discord
from discord.ext import commands

from core import config, dataBase
from core.logger import logger as log


class LeagueOfLegends(commands.Cog):
	def __init__(self):
		self.retry_after = {
			"static-data": time.time(),
			"summoner": time.time(),
			"league": time.time(),
			"match": time.time(),
			"champion": time.time(),
			"champion-mastery": time.time(),
			"other": time.time()
		}
		self.refresh_interval = {
			"static-data": 4320,
			"summoner": 60,
			"league": 300,
			"match": 120,
			"champion": 600,
			"champion-mastery": 600,
			"other": 30
		}

		try:
			keyFile = open("riotKey.txt", "r")
			self.key = keyFile.readline()[:-1]
			keyFile.close()
		except:
			self.key = os.getenv("RIOT_KEY")

			if self.key == None:
				log.error("No Riot Key found. Please save a riotKey.txt or specify a environment variable 'RIOT_KEY'.")

		self.allowed_locales = self.getData("lol/static-data/cdn/languages")["data"]

	def getData(self, name):
		endpoint = "other"

		if name.startswith("lol/static-data"):  # in memory of the static-data-api
			endpoint = "static-data"
		elif name.startswith("lol/champion-mastery"):
			endpoint = "champion-mastery"
		elif name.startswith("lol/platform/v3/champion"):
			endpoint = "champion"
		elif name.startswith("lol/league"):
			endpoint = "league"
		elif name.startswith("lol/match"):
			endpoint = "match"
		elif name.startswith("lol/summoner"):
			endpoint = "summoner"

		fetchtime = dataBase.readVal('lolStat/' + name.lower(), 'fetchtime')
		if (fetchtime > 0) and (fetchtime + self.refresh_interval[endpoint] > time.time()):
			#			print('lolStat/' + name + '.json')
			data = dataBase.dump('lolStat/' + name.lower())
			if data == {}:
				return None
			return data

		elif self.retry_after[endpoint] > time.time():
			log.info('lolStat.getData: timeout. searching for cached results')
			data = dataBase.dump('lolStat/' + name.lower())
			if data == {}:
				return None
			return data

		else:
			if endpoint == "static-data":
				link = "https://ddragon.leagueoflegends.com/" + name[16:] + ".json"
			else:
				link = 'https://euw1.api.riotgames.com/' + name

			log.info('lolStat.getData: downloading {}'.format(link))
			req = urllib.request.Request(link)
			if endpoint != "static-data":
				req.add_header('X-Riot-Token', self.key)
			try:
				url = urllib.request.urlopen(req)
			except urllib.error.HTTPError as e:
				if e.code == 429:
					self.retry_after[endpoint] = time.time() + int(e.headers['Retry-After'])
					log.info('lolStat.getData: got 429: rety after {} seconds. searching for cached results'.format(
						int(e.headers['Retry-After'])))
					data = dataBase.dump('lolStat/' + name.lower())
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
					data = {'data': data}

				data.update({"fetchtime": time.time()})

				filename = 'dataBase/' + "lolStat/" + name + '.json'
				filename = filename.replace("&", "_")
				filename = filename.replace("=", "_")
				filename = filename.replace("?", "_")

				pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

				with open(filename, 'w', encoding='utf-8') as file:
					json.dump(data, file)

				return data

		return None

	@commands.command(no_pm=True)
	async def player_info(self, ctx, *, name: str):
		summoner = name
		summoner = urllib.request.quote(summoner, safe=':/')

		data = await ctx.bot.loop.run_in_executor(None, self.getData,
												  str('lol/summoner/v4/summoners/by-name/' + summoner))
		versions = await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/api/versions')

		locale = config.getLocale(ctx.guild.id)

		if data != None:
			level = data['summonerLevel']
			summoner = data['name']
			icon_id = data['profileIconId']
			version = versions['data'][0]

			embed = discord.Embed(title=summoner)
			embed.set_thumbnail(
				url='https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png'.format(version, icon_id))

			embed.add_field(name=config.strings[locale]['lolStat']['playerInfo_level'], value=level)

			league = self.getData('lol/league/v4/entries/by-summoner/{}'.format(data['id']))
			if league != None:
				for l in league['data']:
					try:
						queueTypeName = config.strings[locale]['lolStat'][l['queueType']]
					except Exception as e:
						log.error("Exception in player_info: " + str(e))
						queueTypeName = l['queueType']
					embed.add_field(name=queueTypeName,
									value='{} {} ({}LP)'.format(l['tier'], l['rank'], l['leaguePoints']))

			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

	@commands.command(no_pm=True)
	async def champion_rotation(self, ctx):
		data = await ctx.bot.loop.run_in_executor(None, self.getData, "lol/platform/v3/champion-rotations")

		locale = config.getLocale(ctx.guild.id)

		versions = await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/api/versions')
		version = versions["data"][0]

		if locale in self.allowed_locales:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/{}/champion".format(
																	 version, locale))
		else:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/en_US/champion".format(
																	 version))

		embed = discord.Embed(title=config.strings[locale]["lolStat"]["championRotationTitle"])

		for champion_id in data["freeChampionIds"]:
			for name in allChampionData["data"]:
				if int(allChampionData["data"][name]["key"]) == int(champion_id):
					championData = allChampionData["data"][name]
					break

			tags = config.strings[locale]["lolStat"][championData["tags"][0]]
			for i in range(1, len(championData["tags"])):
				tags = "{}, {}".format(tags, config.strings[locale]["lolStat"][championData["tags"][i]])

			embed.add_field(name=championData["name"], value=tags)

		await ctx.send(embed=embed)

	@commands.command(no_pm=True)
	async def champion_lore(self, ctx, *, championName: str):
		locale = config.getLocale(ctx.guild.id)

		versions = await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/api/versions')
		version = versions["data"][0]

		if locale in self.allowed_locales:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/{}/champion".format(
																	 version, locale))
		else:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/en_US/champion".format(
																	 version))

		for name in allChampionData["data"]:
			if allChampionData["data"][name]["name"].lower() == championName.lower():
				championName = allChampionData["data"][name]["id"]
				break

		if locale in self.allowed_locales:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/{}/champion/{}".format(
																  version, locale, championName))
		else:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/en_US/champion/{}".format(
																  version, championName))

		if championData != None:
			championData = championData["data"][championName]
			embed = discord.Embed(title=championData["name"])
			embed.add_field(name=championData["title"], value=championData["lore"][:1024])
			embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/{}/{}'.format(version,
																								  championData["image"][
																									  "group"],
																								  championData["image"][
																									  "full"]))
			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

	@commands.command(no_pm=True)
	async def champion_stats(self, ctx, *, championName: str):
		locale = config.getLocale(ctx.guild.id)

		versions = await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/api/versions')
		version = versions["data"][0]

		if locale in self.allowed_locales:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/{}/champion".format(
																	 version, locale))
		else:
			allChampionData = await ctx.bot.loop.run_in_executor(None, self.getData,
																 "lol/static-data/cdn/{}/data/en_US/champion".format(
																	 version))

		for name in allChampionData["data"]:
			if allChampionData["data"][name]["name"].lower() == championName.lower():
				championName = allChampionData["data"][name]["id"]
				break

		if locale in self.allowed_locales:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/{}/champion/{}".format(
																  version, locale, championName))
		else:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/en_US/champion/{}".format(
																  version, championName))

		if championData != None:
			championData = championData["data"][championName]

			tags = config.strings[locale]["lolStat"][championData["tags"][0]]
			for i in range(1, len(championData["tags"])):
				tags = "{}, {}".format(tags, config.strings[locale]["lolStat"][championData["tags"][i]])

			embed = discord.Embed(title=championData["name"] + ", " + championData["title"], description=tags)
			embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/{}/{}'.format(version,
																								  championData["image"][
																									  "group"],
																								  championData["image"][
																									  "full"]))

			for stat_name, stat_value in championData["stats"].items():
				if stat_value > 0 and stat_name != "attackspeedoffset" and stat_name != "attackspeedperlevel":
					try:
						name = config.strings[locale]["lolStat"][str(stat_name)]
					except:
						name = str(stat_name)
					embed.add_field(name=name, value=stat_value)
				elif stat_name == "attackspeedoffset":
					embed.add_field(name=config.strings[locale]["lolStat"]["attackspeed"] + "(Level 1)",
									value=round(0.625 / (1 - (stat_value * -1)), 3))

			spells = [championData["passive"]] + championData["spells"]
			for spell in spells:
				if "tooltip" in spell:
					spellText = spell["tooltip"]
				else:
					spellText = spell["description"]

				if "effectBurn" in spell:
					if spell["effectBurn"][0] != None:
						spellText = spellText.replace("{{ e0 }}", spell["effectBurn"][0])

					for i in range(1, len(spell["effectBurn"])):
						spellText = spellText.replace("{{ e" + str(i) + " }}", spell["effectBurn"][i])

				if "vars" in spell:
					for var in spell["vars"]:
						if isinstance(var["coeff"], list):
							var_text = str(int(round(var["coeff"][0] * 100, 3)))
							for i in range(1, len(var["coeff"])):
								var_text = "{}/{}".format(var_text, str(int(round(var["coeff"][i] * 100, 3))))
						else:
							var_text = str(int(round(var["coeff"] * 100, 3)))

						try:
							link = config.strings[locale]["lolStat"][str(var["link"])]
						except:
							link = str(var["link"])
						var_text = var_text + "% " + link
						spellText = spellText.replace("{{ " + var["key"] + " }}", var_text)

				spellText = re.sub(r"</?br */?>", "\n", spellText)
				# spellText=re.sub(r"</?i>|</?mainText>|</?span[a-zA-Z0-9]*>", "", spellText)
				spellText = re.sub(r"<.+?>", "", spellText)
				spellText = re.sub(r"&nbsp;", " ", spellText)

				if len(spellText) == 0:
					spellText = config.strings[locale]["lolStat"]["champion_data_no_description"]

				spellName = spell["name"]
				if len(spellName) == 0:
					spellName = config.strings[locale]["lolStat"]["champion_data_no_spell_name"]

				embed.add_field(name=spellName, value=spellText, inline=False)

			embed.set_footer(text=config.strings[locale]["lolStat"]["champion_data_disclaimer"])
			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])

	@commands.command(no_pm=True)
	async def champion_tips(self, ctx, *, championName: str):
		locale = config.getLocale(ctx.guild.id)

		versions = await ctx.bot.loop.run_in_executor(None, self.getData, 'lol/static-data/api/versions')
		version = versions["data"][0]

		if locale in self.allowed_locales:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/{}/champion/{}".format(
																  version, locale, championName))
		else:
			championData = await ctx.bot.loop.run_in_executor(None, self.getData,
															  "lol/static-data/cdn/{}/data/en_US/champion/{}".format(
																  version, championName))

		championData = championData["data"][championName]

		if championData != None:
			embed = discord.Embed(title=championData["name"])

			tips = ""
			for tip in championData["allytips"]:
				tips = tips + "\n\n" + tip
			tips = re.sub(r"&nbsp;", " ", tips)
			embed.add_field(name=config.strings[locale]['lolStat']['allytips'], value=tips)

			tips = ""
			for tip in championData["enemytips"]:
				tips = tips + "\n\n" + tip
			tips = re.sub(r"&nbsp;", " ", tips)
			embed.add_field(name=config.strings[locale]['lolStat']['enemytips'], value=tips)

			embed.set_thumbnail(url='https://ddragon.leagueoflegends.com/cdn/{}/img/{}/{}'.format(version,
																								  championData["image"][
																									  "group"],
																								  championData["image"][
																									  "full"]))
			await ctx.send(embed=embed)
		else:
			await ctx.send(config.strings[locale]['lolStat']['lolStat_fail'])


def setup(bot):
	bot.add_cog(LeagueOfLegends())
