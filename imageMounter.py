#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
Python script to MNT Partitions on a Disk Image
http://techanarcy.net
'''
__description__ = 'Python script to MNT Partitions on a Disk Image'
__author__ = 'Kevin Breen'
__version__ = '0.4'
__date__ = '2014/03/07'


import os
import sys
import hashlib
import commands
import subprocess
from datetime import datetime
from optparse import OptionParser, OptionGroup


def main():
	parser = OptionParser(usage='usage: %prog [options] image_name mnt_point\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-s", "--single", action='store_true', default=False, help="Single partition in image")
	parser.add_option("-i", "--info", action='store_true', default=False, help="Just Display the information")
	parser.add_option("-e", "--E", action='store_true', default=False, help="Use ewfmount to mount E0 Evidence Files")
	(options, args) = parser.parse_args()

	if len(args) == 0:
		print "[+] You need to give me some Paths"
		parser.print_help()
		sys.exit()
	# If i just want to print the Disk info
	if options.info == True:
		imageFile = args[0]
		parts = parse_fdisk(imageFile)
		#Need to beautify this
		printInfo(parts)
		sys.exit()
	# If im processing E01 Files
	if options.E == True:
		if len(args) != 2:
			print "[+] You need to specify the image and mount path"
			parser.print_help()
			sys.exit()
		imageFile = args[0]
		mntPath = args[1]
		ewfPath = ewfMount(imageFile)
		if options.single == True:
			mountSinglePart(ewfPath, mntPath)

		elif options.single == False:
			mountMultiPart(ewfPath, mntPath)
		sys.exit()			
	# If my image contains a single parition
	if  options.single == True:
		if len(args) != 2:
			print "[+] You need to specify the image and mount path"
			parser.print_help()
			sys.exit()
		imageFile = args[0]
		mntPath = args[1]
		mountSinglePart(imageFile, mntPath)
	# If my image contains a single parition
	elif  options.single == False:
		if len(args) != 2:
			print "[+] You need to specify the image and mount path"
			parser.print_help()
			sys.exit()
		imageFile = args[0]
		mntPath = args[1]
		mountMultiPart(imageFile, mntPath)
			
def parse_fdisk(img_name):
	# get the output of the fdisk command. 
	try:
		fdiskOutput = commands.getoutput("(fdisk -l %s)"%(img_name))
	except:
		print "[+] Something has gone wrong!"
		sys.exit()
	# partInfo dict will hold all the partitions	
	partInfo = {}
	#Counter to track all partitions
	diskPart = 0
	for line in fdiskOutput.split("\n"):
		# Get sector size we will need this for Offset calculations
		if line.startswith("Units"):
			sector = int(line.split()[6])
		if line.startswith("This doesn't look like a partition table"):
			print "[+] This Doesn't Look like a valid Table."
			print "[+] If this is a single partition try the '-s' option"
			sys.exit()
		if not line.startswith(img_name):
			continue
		# Now get each of our partitions and create a dict of values		
		parts = line.split()
		inf = {}
		if parts[1] == "*":
			inf['Bootable'] = True
			del parts[1]

		else:
			inf['Bootable'] = False
		inf["Sector"] = sector
		inf['Start'] = int(parts[1])
		inf["Offset"] = inf['Start'] * sector
		inf['End'] = int(parts[2])
		inf['Blocks'] = int(parts[3].rstrip("+"))
		inf['Partition_id'] = int(parts[4], 16)
		inf['FileSystem'] = " ".join(parts[5:])

		partInfo[diskPart] = inf
		diskPart += 1
	return diskPart, partInfo



def mountSinglePart(imageFile, mntPath):

	print "[+] Creating Temp Mount Point at %s" % mntPath
	if not os.path.exists(mntPath):
		os.makedirs(mntPath)
	print "[+] Attempting to Mount %s at %s" % (imageFile, mntPath)
	try:
		retcode = subprocess.call("(mount -o ro,loop,show_sys_files,streams_interface=windows %s %s)"%( imageFile, mntPath), shell=True)
		#Crappy error Handling here
		if retcode != 0:
			sys.exit()
		print "[+] Mounted %s at %s" % (imageFile, mntPath)
		print "   [-] To unmount run 'sudo umount %s'" % mntPath
	except:
		print "[+] Failed to Mount %s" % mntPath


def mountMultiPart(imageFile, mntPath):
	print "[+] Checking Partitions"
	count, partitions = parse_fdisk(imageFile)
	print "[+] Found %s partitions" % count
	for i in range(0,count):
		mntPath = mntPath+str(i)
		print "[+] Creating Temp Mount Point at %s" % mntPath
		if not os.path.exists(mntPath):
			os.makedirs(mntPath)
		print "[+] Attempting to Mount Partition %s at %s" % (count, mntPath)
		
		try:
			offset = partitions[i]["Offset"]
			sysType = partitions[i]["FileSystem"]
			if 'HPFS' or 'NTFS' or 'exFAT' in sysTyp
				sysType = "ntfs"
			else:
				sysType = 'ntfs'
			# Add more handling for other format types :)
			retcode = subprocess.call("(mount -t %s -o ro,loop,offset=%s,show_sys_files,streams_interface=windows %s %s)"%(sysType, offset, imageFile, mntPath), shell=True)
			#Crappy error Handling here
			if retcode != 0:
				sys.exit()
			print "[+] Mounted %s at %s" % (imageFile, mntPath)
			print "   [-] To unmount run 'sudo umount %s'" % mntPath
		except:
			print "[+] Failed to Mount %s" % mntPath

def printInfo(parts):
	count = parts[0]
	partitions = parts[1]
	print "[+] There are %s Partitions" % count
	for i in range(0,count):
		print "[+] Partition %s" % i
		print "   [-] Bootable: %s" % partitions[i]["Bootable"]
		print "   [-] FileSystem: %s" % partitions[i]["FileSystem"]
		print "   [-] Start: %s, End: %s" % (partitions[i]["Start"],partitions[i]["End"])
		print "   [-] Calculated Offset: %s" % partitions[i]["Offset"]



def ewfMount(imageFile):
	# Wrapper for ewfmount
	#Check for E01
	if imageFile.endswith(".E01"):
		#make the ewf Mount Point
		# get a unique timestamp
		ts = datetime.now().strftime('%Y_%m_%d-%H_%S')
		ewfPath = "/mnt/ewf4_"+ts
		if not os.path.exists(ewfPath):
			os.makedirs(ewfPath)
		#run ewfmount with our E01 File
		try:
			retcode = subprocess.call("(ewfmount %s %s)"%(imageFile, ewfPath), shell=True)
			#Crappy error Handling here
			if retcode != 0:
				sys.exit()
			print "[+] Mounted E0 Files to %s " % ewfPath+"/ewf1"
			print "   [-] To unmount run 'sudo umount %s'" % ewfPath			
			return ewfPath+"/ewf1"
		except:
			print "[+] Failed to mount E01"
			sys.exit()
	else:
		print "[+] Not a valid E01 File"
		sys.exit()	



if __name__ == "__main__":
	if os.getuid() == 0:
		main()
	else:
		print "[+] You must be Root or Sudo to run this Script"
		sys.exit()
			
			
