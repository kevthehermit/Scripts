#!/usr/bin/env python
'''
VirusTotal Feed Collector
Set your API and change max limit as required
'''

__description__ = 'VT Feed Collector'
__author__ = 'Kevin Breen'
__version__ = '0.1'
__date__ = '2013/10'

import sys
import os
import urllib2
import xml.etree.cElementTree as ET

api_key = 'Your Key Here'
feed_url = 'https://www.virustotal.com/intelligence/hunting/notifications-feed/?key=%s&output=xml' % api_key
max_down = 20

if api_key == 'Your Key Here':
	print "You need to add your own API key"
	sys.exit()
#Pull the XML Feed from VT Int
request = urllib2.Request(feed_url, headers={"Accept" : "application/xml"})
xml = urllib2.urlopen(request)
#Parse the XML 
tree = ET.parse(xml)
root = tree.getroot()
counter = 0
exists = 0
downloads = 0
#Im only interested in rule names and the sha to download


for item in root[0].findall('item'):
	sha256, ruleset, rulename = item.find('title').text.split()
	# create the folder paths
	if not os.path.exists(os.path.join(ruleset, rulename)):
		os.makedirs(os.path.join(ruleset, rulename))
	# if the file already exists dont download again
	if os.path.exists(os.path.join(ruleset, rulename, sha256)):
		print "Hash Already Exists, Passing"
		exists +=1
	#Stay below the max_down count and download
	elif downloads < max_down:
		url = "https://www.virustotal.com/intelligence/download/?hash=%s&apikey=%s" %(sha256, api_key)	
		print "downloading %s" % sha256
		f = urllib2.urlopen(url)
		data = f.read()
		
		# Save each file in to a folder after the rule
		with open(os.path.join(ruleset, rulename, sha256), "wb") as save_file:
			save_file.write(data)
		downloads +=1
	elif downloads > max_down:
		print "Self Imposed Download Limit Reached"
	counter +=1
print "\nTotal Hashes in Feed", counter
print "Files Skipped", exists
print "Files downloaded", downloads		
		
