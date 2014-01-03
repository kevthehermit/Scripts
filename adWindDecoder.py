#!/usr/bin/env python
'''
Adwind Class Decoder
'''

__description__ = 'Adwind Class Decoder'
__author__ = 'Kevin Breen http://techanarchy.net'
__version__ = '0.1'
__date__ = '2014/01'

import sys
import string
import os
from optparse import OptionParser
import zlib

try:
	from Crypto.Cipher import ARC4
	from Crypto.Cipher import DES
except ImportError:
	print "Cannot import PyCrypto, Is it installed?"


def main():
	parser = OptionParser(usage='usage: %prog [options] pass inFile outFile\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-d", "--DES", action='store_true', default=False, help="ENC Mode = DES")
	parser.add_option("-r", "--RC4", action='store_true', default=False, help="ENC Mode = RC4")

	(options, args) = parser.parse_args()
	if len(args) != 3:
		parser.print_help()
		sys.exit()
	password = args[0]
	infile = args[1]
	outfile = args[2]
	
	
	
	with open(outfile, 'w') as out:
		data = open(infile, 'rb').read()

		if options.DES == True:
			result = DecryptDES(password[:8], data)
		elif options.RC4 == True:
			result = DecryptRC4(password, data)
		else:
			print "No Cypher selected"
			sys.exit()
		if infile.endswith(".adwind"):
			result = decompress(result)
			out.write(result)
		else:
			result = filter(lambda x: x in string.printable, result)
			out.write(result)

#### DES Cipher ####		
		
def DecryptDES(enckey, data):
	cipher = DES.new(enckey, DES.MODE_ECB) # set the ciper
	return cipher.decrypt(data) # decrpyt the data
	
####RC4 Cipher ####	
def DecryptRC4(enckey, data):
	cipher = ARC4.new(enckey) # set the ciper
	return cipher.decrypt(data) # decrpyt the data



#### ZLIB ####

def decompress(data):
	ba = bytearray(data)
	this = zlib.decompress(bytes(data), 15+32)
	return this
if __name__ == "__main__":
	main()