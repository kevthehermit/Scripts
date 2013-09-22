#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
Python script to scan SMB / FTP results parsed from shodan
'''
__description__ = 'Shodan SMB / FTP Parser'
__author__ = 'Kevin Breen'
__version__ = '0.3'
__date__ = '2013/09/20'

# Configuration
API_KEY = "ENTERYOURAPIKEYHERE" # REMOVE ME BEFORE POSTING TO GIT
client_machine_name = 'Random Name'
remote_machine_name = 'server'

import os
import sys
from optparse import OptionParser
from ftplib import FTP
try:
	import shodan
except:
	print "Shodan Not Found please install using 'pip install shodan'"
try:
	from smb.SMBConnection import SMBConnection
except:
	print "pySMB Not Found please install using 'pip install pysmb'"


def main():
	parser = OptionParser(usage='usage: %prog [options] "search term" outfile\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-t", dest="searchType", help="Search Type. e.g. SMB")
	(options, args) = parser.parse_args()
	searchTerm = args[0]
	searchType = options.searchType
	outfile = args[1]
	if len(args) != 2:
		parser.print_help()
		sys.exit()
	
	if args[0] == "":
		parser.print_help()
		sys.exit()
	if options.searchType == "SMB":
		print "Running Query: ", searchTerm
		ipList = shodanSearch().collectIP(searchTerm)
		smbParse().createList(ipList, outfile)

	elif options.searchType == "FTP":
		print "Running Query: ", searchTerm
		ipList = shodanSearch().collectIP(searchTerm)
		ftpParse().ftpList(ipList, outfile)
	else:
		print "not a valid search type: ", options.searchType
		parser.print_help()
		sys.exit()
	
class shodanSearch():
	def collectIP(self, searchString):
		ip_address = []
		try:			
			# Setup the api
			api = shodan.WebAPI(API_KEY)
			# Perform the search
			query = searchString
			result = api.search(query)
			print 'Results found: %s' % result['total']
			# Loop through the matches and print each IP
			for host in result['matches']:
					ip_address.append(host['ip'])
		except Exception, e:
				print 'Error: %s' % e
				sys.exit(1)
		return ip_address	
	
class ftpParse():
	def ftpList(self, ipList, outfile):
		temp = sys.stdout
		with open(outfile, 'a') as out: #Open our save file	
			for ip in ipList:
				sys.stdout = temp
				print "Connecting to FTP: %s" % ip
				out.write("Connecting to FTP: %s \n" % ip)
				try:
					ftp = FTP(ip) # Connect to FTP
					ftp.login() # Try Anonymous Login
					lines = ftp.retrlines('LIST') # Grab the Dir Listing
					print "Collecting File Names"
					sys.stdout = out # redirect stdout to save file so we can store the Dir List
					out.write(lines)
					out.write('\n')
					sys.stdout = temp #restore print commands to interactive prompt
				except:
					print "Failed to connect to FTP: %s" % ip
					out.write("Failed to connect to IP: %s \n" % ip)

class smbParse():
	def createList(self, ipList, outfile):
		with open(outfile, 'a') as out:
			for ip in ipList:
				out.write("\n----------------------------------------------------\n")
				print "Attempting to access: ", ip
				out.write("Attempting to access: %s \n" % ip)
				try:
					conn = SMBConnection('guest', '', client_machine_name, remote_machine_name, use_ntlm_v2 = True)
					conn.connect(ip, 139)
					print "Connected to: ", ip
					out.write("Connected To: %s \n" % ip)
				except:
					print "Failed to Connect"
					out.write("Failed to Connect To: %s \n" % ip)
					pass
				try:
					shareList = conn.listShares()
				except:
					out.write("Failed to open Shares\n")
					shareList = None
				if shareList != None:
					for x in shareList:
						try:
							out.write("found Share: %s \n" % x.name)
							print "Listing files in share: ", x.name
							out.write("Listing files in share: %s \n" % x.name)
							filelist = conn.listPath(x.name, '/')
							for y in filelist:
								if y.isDirectory:
									print "DIR", y.filename
								out.write("-----")
								out.write(y.filename)
								out.write('\n')
						except:
							print "failed to open share: ", x.name
							out.write("Failed to open Share: %s \n" % x.name)

		print "report written to outfile.txt"
		
	
if __name__ == "__main__":
	main()