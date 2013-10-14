#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
jRat Config Parser

'''
__description__ = 'jRat Config Parser'
__author__ = 'Kevin Breen'
__version__ = '0.1'
__date__ = '2013/08/05'

import sys
import base64
import string
from zipfile import ZipFile
from optparse import OptionParser
try:
	from Crypto.Cipher import AES
	from Crypto.Cipher import DES3
except ImportError:
	print "Cannot import PyCrypto, Is it installed?"


def main():
	parser = OptionParser(usage='usage: %prog [options] InFile SavePath\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-v", "--verbose", action='store_true', default=False, help="Verbose Output")
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit()

	archive = args[0]
	outfile = args[1]
	dropper = None
	conf = None
	with ZipFile(archive, 'r') as zip:
		for name in zip.namelist():
			if name == "key.dat":
				enckey = zip.read(name)
			if name == "enc.dat":				
				dropper = zip.read(name)
			if name == "config.dat":
				conf = zip.read(name)
		if dropper != None:
			print "Dropper Detected"
			ExtractDrop(enckey, dropper, outfile)
		elif conf != None:
			if len(enckey) == 16:
				cleandrop = DecryptAES(enckey, conf)
				WriteReport(enckey, outfile, cleandrop)
			elif len(enckey) == 24:
				cleandrop = DecryptDES(enckey, conf)
				WriteReport(enckey, outfile, cleandrop)

def ExtractDrop(enckey, data, outfile):
	split = enckey.split('\x2c')
	key = split[0][:16]
	print "### Dropper Information ###"
	for x in split:
		try:
			print base64.b64decode(x).decode('hex')
		except:
			print base64.b64decode(x[16:]).decode('hex')
	newzipdata = DecryptAES(key, data)
	from cStringIO import StringIO
	newZip = StringIO(newzipdata)
	with ZipFile(newZip) as zip:
		for name in zip.namelist():
			if name == "key.dat":
				enckey = zip.read(name)
			if name == "config.dat":
				conf = zip.read(name)
			if len(enckey) == 16:
				printkey = enckey.encode('hex')
				print "AES Key Found: ", printkey
				cleandrop = DecryptAES(enckey, conf)
				print "### Configuration File ###"
				WriteReport(enckey, outfile, cleandrop)
			elif len(enckey) == 24:
				printkey = enckey
				print "DES Key Found: ", enckey
				cleandrop = DecryptDES(enckey, conf)
				print "### Configuration File ###"
				WriteReport(enckey, outfile, cleandrop)
				
def DecryptAES(enckey, data):					
		cipher = AES.new(enckey)
		return cipher.decrypt(data)
		
def DecryptDES(enckey, data):

		cipher = DES3.new(enckey)
		return cipher.decrypt(data)

def WriteReport(key, outfile, data):		
	split = data.split("SPLIT")
	with open(outfile, 'a') as new:
		new.write(key)
		new.write('\n')
		for s in split:
			stripped = (char for char in s if 32 < ord(char) < 127)
			line = ''.join(stripped)
			#if options.verbose == True:
			print line
			new.write(line)
			new.write('\n')
	print "Config Written To: ", outfile


if __name__ == "__main__":
	main()