#!/usr/bin/env python
'''
Bozok Config Extractor
'''

__description__ = 'Bozok Config Extractor'
__author__ = 'Kevin Breen http://techanarchy.net'
__version__ = '0.2'
__date__ = '2013/11'

import re
import os
import sys
from optparse import OptionParser


def main():
	parser = OptionParser(usage='usage: %prog [options] inFile outConfig\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-r", "--recursive", action='store_true', default=False, help="Recursive Mode")
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit()

	if options.recursive == True:
		with open(args[1], 'a+') as out:
			out.write("Filename,ServerID,Mutex,InstallName,Startup Name,Extension,Password,Install Flag,Startup Flag,Visible Flag,Unknown Flag,Unknown Flag,Port,Domain,Unknown Flag\n")	
			for server in os.listdir(args[0]):
				config = configExtract(os.path.join(args[0], server))
				if config != None:
					out.write((server+','))
					for column in config:
						out.write((column+','))
					out.write('\n')
	else:
		with open(args[1], 'a+') as out:
			out.write("Filename,ServerID,Mutex,InstallName,Startup Name,Extension,Password,Install Flag,Startup Flag,Visible Flag,Unknown Flag,Unknown Flag,Port,Domain,Unknown Flag\n")	
			config = configExtract(args[0])
			if config != None:
				out.write((args[0]+','))
				for column in config:
					out.write((column+','))
				out.write('\n')

def configExtract(server):
	openfile = open(server, 'rb').read() # Open and read the server
	try:
		match = re.findall('O\x00\x00\x00(.+)\|\x00\x00\x00', openfile) # find the config section
		clean_config = match[0].replace('\x00', '') # replace all wide null chars
		config = clean_config.split('|') # split on our |
		return config		
	except:
		print "Couldn't Locate the Config, Is it Packed?"
		

		
if __name__ == "__main__":
	main()