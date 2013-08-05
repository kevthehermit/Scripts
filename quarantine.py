#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
McAfee Quarnatine Extractor
'''

__description__ = 'Python script to extract McAfee Quarantine Files'
__author__ = 'Kevin Breen'
__version__ = '0.1'
__date__ = '2013/08/05'

import os
import sys
import subprocess
from optparse import OptionParser

def main():
	parser = OptionParser(usage='usage: %prog [options] bupFile savePath\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-k", "--key", dest="key", default=0x6A, help="Optional XOR Key Default is 0x6A")
	(options, args) = parser.parse_args()
	if len(args) !=2:
		parser.print_help()
		sys.exit()
	bupFile = args[0]
	savePath = args[1]
	key = options.key
	if not os.path.exists(savePath):
		os.makedirs(savePath)
	try:
		subprocess.call(["7z", "e", args[0]])
	except:
		print "Failed to extract is 7z installed?"
		sys.exit()
	encodedA = bytearray(open('Details', 'rb').read())
	for i in range(len(encodedA)):
		encodedA[i] ^= key
	open(os.path.join(savePath, 'Details.txt'), 'wb').write(encodedA)
	
	encodedB = bytearray(open('File_0', 'rb').read())
	for i in range(len(encodedB)):
		encodedB[i] ^= key
	open(os.path.join(savePath, 'File_0.xor'), 'wb').write(encodedB)
	
	os.remove('Details')
	os.remove('File_0')
	
if __name__ == "__main__":
	main()