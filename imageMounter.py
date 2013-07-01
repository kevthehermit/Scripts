#!/usr/bin/env python
'''
Copyright (C) 2013 Kevin Breen.
DiskMount

'''
__description__ = 'Python script to MNT, and optionally Hash all files from a Disk Image'
__author__ = 'Kevin Breen'
__version__ = '0.2'
__date__ = '2013/06/30'


import os
import sys
import hashlib
import commands
import subprocess
from datetime import datetime
from optparse import OptionParser, OptionGroup


def main():
	parser = OptionParser(usage='usage: %prog [options] image_name mnt_point\n' + __description__, version='%prog ' + __version__)
	parser.add_option("-m", "--md5", action='store_true', default=False, help="MD5 Each File")
	parser.add_option("-s", "--ssdeep", action='store_true', default=False, help="ssdeep Each File")
	parser.add_option("-o", "--output", dest='outFile', help="Output CSV File")
	(options, args) = parser.parse_args()
	if len(args) != 2:
		parser.print_help()
		sys.exit()
	imageName = args[0]
	rootDir = args[1]
	outFile = options.outFile
	counter = 0
	startTime = datetime.now()
	mounts = mountImage().parse_fdisk(imageName, rootDir)
	if (options.md5 or options.ssdeep) and not options.outFile:
		parser.error("You must Specify an output file")
		parser.print_help()
		sys.exit()
	if (options.md5 or options.ssdeep) and options.outFile:
		for mnt_point in mounts:
			print "Hashing Mount Point %s "% (mnt_point)
			for path, subdirs, files in os.walk(mnt_point):
				for names in files:
					counter += 1
					pathName = os.path.join(path, names)
					md5, deep = hashing().fileHash(pathName, options.md5, options.ssdeep)
					string = ("%s, %s, %s\n" % (pathName, md5, deep))
					reportMain(outFile, string)
		umountChoice = raw_input("Do you wish to unmount: y/n")
		if umountChoice != "y" or umountChoice != "n":
			umountChoice = raw_input("Do you wish to unmount: y/n")
		elif umountChoise == "y":				
			subprocess.call("(umount %s)"%(mnt_point), shell=True)
			os.rmdir(mnt_point)
		elif umountChoice == "n":
			pass
	endTime = datetime.now() - startTime
	print endTime
	print counter

				
class hashing:
	def fileHash(self, filePath, mdHash, deepHash):
		try:
			with open(filePath, 'rb') as fh:
				data = fh.read()
		except:
			print "unable to open file %s" % filePath
			data = None
		if data != None and mdHash == True:
			m = hashlib.md5()
			m.update(data)
			md5 = m.hexdigest()
		else:
			md5 = "Null"
		if data != None and deepHash == True:
			import ssdeep
			deep = ssdeep.hash(data)
		else:
			deep = "Null"
		return md5, deep

		
class reportMain:
	def __init__(self, outFile, string):
		with open(outFile, "a") as f:
			f.write(string)
			

class mountImage:
	def parse_fdisk(self, img_name, mnt_location):
		fdisk_output = commands.getoutput("(fdisk -l %s)"%(img_name))
		print img_name
		result = {}
		mounts = []
		diskPart = 0
		for line in fdisk_output.split("\n"):
			if line.startswith("Units"):
				sector = int(line.split()[6])
			if not line.startswith(img_name): continue
			diskPart += 1
			parts = line.split()
			inf = {}
			if parts[1] == "*":
				inf['bootable'] = True
				del parts[1]

			else:
				inf['bootable'] = False

			inf['start'] = int(parts[1])
			offset = inf['start'] * sector
			inf['end'] = int(parts[2])
			inf['blocks'] = int(parts[3].rstrip("+"))
			inf['partition_id'] = int(parts[4], 16)
			inf['partition_id_string'] = " ".join(parts[5:])
			mnt_path = mnt_location + str(diskPart)
			mountChoice = raw_input("Do you wish to mount: y/n")

			if mountChoice == "n":				
				continue
			elif mountChoice == "y":

				print "Creating Temp Mount Points at %s" % mnt_path
				if not os.path.exists(mnt_path):
					os.makedirs(mnt_path)
				try:
					retcode = subprocess.call("(mount -t ntfs -o ro,loop,offset=%s %s %s)"%(offset, img_name, mnt_path), shell=True)
					mounts.append(mnt_path)
				except:
					print "Failed to Mount %s" % mnt_path
			

				result[parts[0]] = inf
		for disk, info in result.items():
			string = (disk, " ".join(["%s=%r" % i for i in info.items()]))
		return mounts

if __name__ == "__main__":
	main()
			
