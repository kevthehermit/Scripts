#!/usr/bin/env python
'''
Bozok Config Extractor
'''

__description__ = 'Bozok Config Extractor'
__author__ = 'Kevin Breen http://techanarchy.net'
__version__ = '0.1'
__date__ = '2013/11'

import re
import sys
from optparse import OptionParser

parser = OptionParser(usage='usage: %prog [options] inFile outConfig\n' + __description__, version='%prog ' + __version__)

(options, args) = parser.parse_args()
if len(args) != 2:
	parser.print_help()
	sys.exit()
	
server = args[0]
openfile = open(server, 'rb').read() # Open and read the server
try:
	match = re.findall('O\x00\x00\x00(.+)\|\x00\x00\x00', openfile) # find the config section
	raw_config = match[0].replace('\x00', '') # replace all wuide null chars
	clean_config = raw_config.split('|') # split on our |
	with open(args[1], 'w+') as out:# write each section to file
		out.write(("ServerID = " + clean_config[0] + '\n'))
		out.write(("Mutex = " + clean_config[1] + '\n'))
		out.write(("Install Name = " + clean_config[2] + '\n'))
		out.write(("Startup Name = " + clean_config[3] + '\n'))
		out.write(("Extension = " + clean_config[4] + '\n'))
		out.write(("Password = " + clean_config[5] + '\n'))
		out.write(("Install Flag = " + clean_config[6] + '\n'))
		out.write(("StartUp Flag = " + clean_config[7] + '\n'))
		out.write(("Visible Flag = " + clean_config[8] + '\n'))
		out.write(("Unknown Flag = " + clean_config[9] + '\n'))
		out.write(("Unknown Flag = " + clean_config[10] + '\n'))
		out.write(("Port = " + clean_config[11] + '\n'))
		out.write(("Domain = " + clean_config[12] + '\n'))
		out.write(("Unknown Flag = " + clean_config[13] + '\n'))
		print "Config Written to", args[1]
except:
	print "Couldn't Locate the Config, Is it Packed?"

