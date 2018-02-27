from discord.ext import commands
import dataBase
import config

import urllib.request
import json
import time

class LeagueOfLegends:
	def __init__(self, bot):
		self.bot=bot
		self.lastrun=time.time()
		keyFile=open("riotKey.txt", "r")
		self.key=keyFile.readline()
		keyFile.close()

	def getDataByName(self, name, apiLink):
#		global lastrun

		fetchtime=dataBase.readVal('lolStat/summoner/' + name.lower(), 'fetchtime')
		if (fetchtime > 0) and (fetchtime+300 > time.time()):
			data=dataBase.dump('lolStat/summoner/' + name.lower())
			if data == {}:
				return {'lolStatStatus' : 'failed'}
			else:
				data.update({'lolStatStatus' : 'cache'})
			return data

		elif self.lastrun+4 > time.time():
			print('timeout. searching for cached results')
#			await client.send_message(message.channel, 'Nur ein Request alle 4 Sekunden möglich.')
			data=dataBase.dump('lolStat/summoner/' + name.lower())
			if data == {}:
				return {'lolStatStatus' : 'failed'}
			else:
				data.update({'lolStatStatus' : 'cache'})
			return data

		else:
			link='https://euw1.api.riotgames.com' + apiLink + '/by-name/' + name + '?api_key=' + self.key
#			print(link)
			with urllib.request.urlopen(link) as url:
				self.lastrun=time.time()
				data = json.loads(url.read().decode())

				for keyName in data.keys():
					dataBase.writeVal('lolStat/summoner/' + name.lower(), keyName, data[keyName])
				dataBase.writeVal('lolStat/summoner/' + name.lower(), 'fetchtime', time.time())

				data.update({'lolStatStatus' : 'success'})
				return data

		return {'lolStatStatus' : 'failed'}

#	@commands.command(description='Get the lummoner-level in League of Legends', pass_context=True)
	@commands.command(description=config.strings['lolStat']['lstatlevel_description'], pass_context=True)
	async def lstatlevel(self, ctx, name : str):
		summoner=name
		summoner=urllib.request.quote(summoner, safe=':/')

		data=self.getDataByName(summoner, '/lol/summoner/v3/summoners')
#		print(data)

		if data['lolStatStatus'] == 'success':
			level=data['summonerLevel']
			summoner=data['name']

#			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level))
			await ctx.send(config.strings['lolStat']['lstatlevel_msg'].format(summoner, str(level)))
		elif data['lolStatStatus'] == 'cache':
			level=data['summonerLevel']
			summoner=data['name']

#			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level) + '. (Aus Datenbank gelesen)')
			await ctx.send(config.strings['lolStat']['lstatlevel_msg'].format(summoner, str(level)))
		elif data['lolStatStatus'] == 'timeout':
			level=data['summonerLevel']
			summoner=data['name']

#			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level) + '. (Aus Datenbank gelesen wegen Timeout)')
			await ctx.send(config.strings['lolStat']['lstatlevel_msg'].format(summoner, str(level)))
		else:
#			await ctx.send('Fehler bei der Abfrage')
			await ctx.send(config.strings['lolStat']['lstatlevel_fail'])

def setup(bot):
	bot.add_cog(LeagueOfLegends(bot))
