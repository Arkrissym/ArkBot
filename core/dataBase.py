# MIT License

# Copyright (c) 2017-2019 Arkrissym

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os
import pathlib

from core.logger import logger as log


def dump(prefix):
	filename = 'dataBase/' + prefix + '.json'
	filename = filename.replace("&", "_")
	filename = filename.replace("=", "_")
	filename = filename.replace("?", "_")

	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
			data = json.load(file)
			return data
	except FileNotFoundError:
		return {}
	except Exception as e:
		log.error("dataBase - Cannot read (dump) data: " + str(e))
		return {}
	return {}


def readVal(prefix, valName):
	filename = 'dataBase/' + prefix + '.json'
	filename = filename.replace("&", "_")
	filename = filename.replace("=", "_")
	filename = filename.replace("?", "_")

	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
			data = json.load(file)
			for key in data.keys():
				if key == valName:
					return data[valName]
	except FileNotFoundError:
		return 0
	except Exception as e:
		log.error("dataBase - Cannot read data: " + str(e))
		return 0
	return 0


def writeVal(prefix, valName, val):
	filename = 'dataBase/' + prefix + '.json'
	filename = filename.replace("&", "_")
	filename = filename.replace("=", "_")
	filename = filename.replace("?", "_")

	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
			data = {}
			data = json.load(file)
			file.close()
	except FileNotFoundError:
		data = {}
	except:
		return 0

	try:
		with open(filename, 'w', encoding='utf-8') as file:
			data.update({valName: val})
			json.dump(data, file)
			return 1
	except Exception as e:
		log.error("dataBase - Cannot write data: " + str(e))
		return 0


def deleteVal(prefix, valName):
	filename = 'dataBase/' + prefix + '.json'
	filename = filename.replace("&", "_")
	filename = filename.replace("=", "_")
	filename = filename.replace("?", "_")

	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
			data = {}
			data = json.load(file)
			file.close()
	except FileNotFoundError:
		data = {}
	except:
		return 0

	try:
		with open(filename, 'w', encoding='utf-8') as file:
			del data[valName]
			json.dump(data, file)
			return 1
	except Exception as e:
		log.error("dataBase - Cannot delete data: " + str(e))
		return 0
