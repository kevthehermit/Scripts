#!/usr/bin/env python
'''
Copyright (C) 2012-2013 Kevin Breen.
YaraMail
Python script to YaraScan Email Attatchments
'''
__description__ = 'Yara Mail Scanner, use it to Scan Email Attatchments'
__author__ = 'Kevin Breen'
__version__ = '0.3'
__date__ = '2013/04/22'


import os
import sys
import hashlib
from datetime import datetime
from optparse import OptionParser, OptionGroup


def main():
	parser = OptionParser(usage='usage: %prog [options] root output\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-m", "--md5", action='store_true', default=False, help="MD5 Each File")
	parser.add_option("-s", "--ssdeep", action='store_true', default=False, help="ssdeep Each File")
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit()
	rootDir = args[0]
	outFile = args[1]
	counter = 0
	startTime = datetime.now()
	for path, subdirs, files in os.walk(rootDir):
		for names in files:
			counter += 1
			pathName = os.path.join(path, names)
			md5, deep = hashing().fileHash(pathName)
			print pathName, md5, deep
			reportMain(outFile, pathName, md5, deep)
	endTime = datetime.now() - startTime
	print endTime
	print counter

				
class hashing:
	def fileHash(self, filePath):
		
		try:
			with open(filePath, 'rb') as fh:
				data = fh.read()
			m = hashlib.md5()
			m.update(data)
			md5 = m.hexdigest()
			try:
				import ssdeep
				deep = ssdeep.hash(data)
			except:
				deep = "Null"
		except:
			md5 = "Null"
			deep = "Null"
		return md5, deep

		
class reportMain:
	def __init__(self, outFile, pathName, md5, deep):
		with open(outFile, "a") as f:
			f.write("%s, %s, %s\n" % (pathName, md5, deep))
			
if __name__ == "__main__":
	main()