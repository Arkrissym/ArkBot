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

import json
import pathlib
import os
import psycopg2

def dump(prefix):
	filename='dataBase/' + prefix + '.json'
	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
			data=json.load(file)
			return data
	except:
		return {}
	return {}

def readVal(prefix, valName):
	filename='dataBase/' + prefix + '.json'
	pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)

	try:
		with open(filename, 'r', encoding='utf-8') as file:
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
		with open(filename, 'r', encoding='utf-8') as file:
			data={}
			data=json.load(file)
			file.close()
	except FileNotFoundError:
		data={}
	except:
		return 0

	try:
		with open(filename, 'w', encoding='utf-8') as file:
			data.update({valName : val})
			json.dump(data, file)
			return 1
	except:
		return 0

def sqlReadRow(name):
	conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
	cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
	cur.execute("SELECT * FROM config")
	
	count = 0
	for row in cur:
		print("row " + str(count) + ": " + row)
		count += 1
		if row[0] == name:
			return row

	return None

def sqlWriteRow(name, row):
	conn=psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
	cur=conn.cursor("dataBase_cursor", cursor_factory=psycopg2.extras.DictCursor)
	
	sql_string="""
		INSERT INTO config (name{})
		VALUES ({}{})
		"""

	names = ""
	vals = ""
	count = 0
	for val in row:
		names = names + ", value" + str(count)
		vals = vals + ", " + val
		count += 1

	cur.execute(sql_string)
	
	return 1
