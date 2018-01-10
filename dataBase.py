import json

def readVal(user, valName):
	try:
		with open('dataBase/' + user + '.json', 'r') as file:
			data=json.load(file)
			for key in data.keys():
				if key == valName:
					return data[valName]
	except:
		return 0
	return 0

def writeVal(user, valName, val):
	try:
		with open('dataBase/' + user + '.json', 'r') as file:
			data={}
			data=json.load(file)
			file.close()
	except FileNotFoundError:
		data={}
	except:
		return 0

	try:
		with open('dataBase/' + user + '.json', 'w') as file:
#			file.write('[')
			data.update({valName : val})
			json.dump(data, file)
#			file.write(']')
			return 1
	except:
		return 0
