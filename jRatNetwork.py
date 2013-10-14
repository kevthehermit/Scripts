#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
jRat Network Decrypter

'''
__description__ = 'jRat Config Parser'
__author__ = 'Kevin Breen'
__version__ = '0.1'
__date__ = '2013/08/05'

import sys
import re
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
	parser = OptionParser(usage='usage: %prog [options] keyFile DataFile -o <Offset> -s <SaveFile>\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-v", action='store_true', default=False, help="Verbose Output")
	parser.add_option("-o", dest="offset", default=0, help="Optional Offset")
	parser.add_option("-s", dest='outfile', help="OutPut Save File")
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit()


	keyFile = args[0]
	dataFile = args[1]
	enckey = open(keyFile, 'rb').read()
	f = open(dataFile, 'rb').read().replace("\x00", "")
	stream = bytearray(f)
	EOF = len(stream)
	Offset = int(options.offset)
	outfile = options.outfile
	if len(enckey) == 16:
		printkey = enckey.encode('hex')
		print "AES Key Found: ", printkey	
		report = AESDecrypt(enckey, stream, Offset, EOF)
		if options.outfile:
			writereport(outfile, report)
	elif len(enckey) == 24:
		printkey = enckey
		print "DES Key Found: ", enckey
		report = DESDecrypt(enckey, stream, Offset, EOF)
		if options.outfile:
			writereport(outfile, report)
	else:
		print "Unknown Key Length Found"
		sys.exit()

	#with open('sample2clean.bin', 'a') as clean:
	#	clean.write(f)

def AESDecrypt(enckey, stream, Offset, EOF):
	cipher = AES.new(enckey)
	report = []
	counter = 11
	while Offset < EOF:
		print "off: ", Offset
		Length = stream[Offset]
		'''if counter != 0:
			Offset += 1
			print "off: ", Offset
			Length = stream[Offset]
			counter -= 1
			print counter'''
		if Length == 21 or Length == 31 :
			Offset += 1
			Length = stream[Offset]
		print "len: ", Length
		this = []

		for l in range(Offset+1,Offset+1+Length):
			this.append(chr(stream[l]))

		predecode =  "".join(this)
		print predecode
		try:
			if predecode.startswith("-h"):
				decstring = predecode[3:].decode('hex')
			else:
				string = base64.b64decode(predecode)
				decstring = cipher.decrypt(string)
			clean = (char for char in decstring if 31 < ord(char) < 127)
			line = ''.join(clean)
			print line
			report.append(line)
			Offset += (Length+1)
		except:
			Offset += (Length+1)
	return report


def DESDecrypt(enckey, stream, Offset, EOF):
	cipher = DES3.new(enckey)
	report = []
	while Offset < EOF:
		#print "off: ", Offset
		Length = stream[Offset]
		#print "len: ", Length
		this = []
		for l in range(Offset+1,Offset+1+Length):
			this.append(chr(stream[l]))
		predecode =  "".join(this)
		#print predecode
		if predecode.startswith("-h"):
			decstring = predecode[3:].decode('hex')
		else:
			string = base64.b64decode(predecode)
			decstring = cipher.decrypt(string)
		clean = (char for char in decstring if 31 < ord(char) < 127)
		line = ''.join(clean)
		report.append(line)
		Offset += (Length+1)
	return report

def writereport(outfile, report):
	with open(outfile, 'w') as reportFile:
		for line in report:
			reportFile.write(line)
			reportFile.write('\n')
	print "Report Written to: ", outfile
		
if __name__ == "__main__":
	main()