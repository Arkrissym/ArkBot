import json
import pathlib
import os

def readVal(user, channel, valName):
	if hasattr(channel, 'server'):
		server='/' + str(channel.server) + '/' + str(channel) + '/'
	else:
		server='/'

	filename='dataBase' + server + user + '.json'
	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r') as file:
			data=json.load(file)
			for key in data.keys():
				if key == valName:
					return data[valName]
	except:
		return 0
	return 0

def writeVal(user, channel, valName, val):
	if hasattr(channel, 'server'):
		server='/' + str(channel.server) + '/' + str(channel) + '/'
	else:
		server='/'

	filename='dataBase' + server + user + '.json'
	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r') as file:
			data={}
			data=json.load(file)
			file.close()
	except FileNotFoundError:
		data={}
	except:
		return 0

	try:
		with open(filename, 'w') as file:
			data.update({valName : val})
			json.dump(data, file)
			return 1
	except:
		return 0
