import os
import sys
import commands
import subprocess
import json
from optparse import OptionParser

def main():
    parser = OptionParser(usage='Usage: %prog [options] pcapfile')
    parser.add_option("-l", "--language", default="gb", help="Keyboard Language")
    parser.add_option("-a", "--address", help="USB Device Address")
    (options, args) = parser.parse_args()
    
    if len(args) == 0:
        print "[+] You need to provide a pcap file"
        sys.exit()
        
    if not options.address:
        print "[!] You need to privide a USB Device Address"
        sys.exit()
        
    tshark_output = commands.getoutput('tshark -r {0} -T fields -e usb.capdata -R "usb.capdata != 00:00:00:00:00:00:00:00 && usb.transfer_type == 0x01 && usb.device_address=={1}" -2'.format(args[0], options.address))
    # 

    # tshark -r Keylogger.pcapng -T fields -e usb.capdata -R "usb.device_address==10" -2 > keystrokes.txt

    duck_lang = 'gb'
    out_file = ''

    # Read in Langauge File
    lang_file = json.load(open('gb.json'))

    # Format tshark output
    for line in tshark_output.split('\n'):
        try:
            key_codes = line.split(':')
        except:
            key_codes = False
            
            
        # Create compatible keymap
        if key_codes and len(key_codes) > 3 and key_codes[3] == '00':
            
            if key_codes[0] == '20':
                key_codes[0] = '02'
            
            keymap = ''
            keymap += key_codes[0]
            keymap += ','
            keymap += key_codes[1]
            keymap += ','
            keymap += key_codes[2]
            
            keymap_char = ''
            for key, value in lang_file.iteritems():
                
                if keymap == value:
                    keymap_char = key
                    if key == 'SPACE':
                        keymap_char = ' '
                    elif key == 'ENTER':
                        keymap_char = '\n'
                    elif key == 'SHIFT':
                        keymap_char = ''
                        
                    
            if keymap_char:        
                out_file += keymap_char
            else:
                print "Unmapped Key Found: ", key_codes
    
    print "Captured KeyStrokes\n"
    print out_file
    print "End Captured Session"



if __name__ == "__main__":
    main()



