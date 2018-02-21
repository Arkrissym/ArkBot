import json
import pathlib
import os

def dump(prefix):
	filename='dataBase/' + prefix + '.json'
	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r') as file:
			data=json.load(file)
			return data
	except:
		return {}
	return {}

def readVal(prefix, valName):
	filename='dataBase/' + prefix + '.json'
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

def writeVal(prefix, valName, val):
	filename='dataBase/' + prefix + '.json'
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
