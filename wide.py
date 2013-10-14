import base64
from Crypto.Cipher import AES
import re
keyFile = "keyAES.dat"
#configFile = "config.dat"

enckey = open(keyFile, 'rb').read()
#conf = open(configFile, 'rb').read()
#new = enckey.encode('hex')

cipher = AES.new(enckey)

with open('raw-stream2.hex', 'rb') as f:
	f1 = re.findall( b'\x00\x18\x00(.{47}?)|\x00\x40\x00(.{127}?)|\x00\x2C\x00(.{87}?)|\x00\x81\x00\x2d\x00\x68\x00\x20(.{252}?)|\x00\x6f\x00\x2d\x00\x68\x00\x20(.{216}?)|\x00\x70\x00\x2d\x00\x68\x00\x20(.{222}?)', f.read())

for x in f1:
	for y in x:
		if y != "":
		
			string = base64.b64decode(y)
			decstring = cipher.decrypt(string)
			with open('outnewish.txt', 'a') as out:
				stripped = (char for char in decstring if 31 < ord(char) < 127)
				line = ''.join(stripped)
				out.write(line)
				out.write('\n')
	print decstring, '\n'



#decConfig = cipher.decrypt(conf)



