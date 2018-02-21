from discord.ext import commands
import dataBase

import urllib.request
import json
import time

class LeagueOfLegends:
	def __init__(self, bot):
		self.bot=bot
		self.lastrun=time.time()
		self.key='RGAPI-329eb39d-5235-4a5b-adfc-0d8d3a69209b'

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

	@commands.command(description='Get the lummoner-level in League of Legends', pass_context=True)
	async def lstatlevel(self, ctx, name : str):
		summoner=name
		summoner=urllib.request.quote(summoner, safe=':/')

		data=self.getDataByName(summoner, '/lol/summoner/v3/summoners')
#		print(data)

		if data['lolStatStatus'] == 'success':
			level=data['summonerLevel']
			summoner=data['name']

			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level))
		elif data['lolStatStatus'] == 'cache':
			level=data['summonerLevel']
			summoner=data['name']

			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level) + '. (Aus Datenbank gelesen)')
		elif data['lolStatStatus'] == 'timeout':
			level=data['summonerLevel']
			summoner=data['name']

			await ctx.send('Spieler ' + summoner + ' ist Level ' + str(level) + '. (Aus Datenbank gelesen wegen Timeout)')
		else:
			await ctx.send('Fehler bei der Abfrage')

def setup(bot):
	bot.add_cog(LeagueOfLegends(bot))
