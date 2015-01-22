import re
import sys
import operator
from optparse import OptionParser

def clean_comments(line):
    return re.sub('/\*(.*?)\*/', '', line)

def find_split(all_text):
    split_chars = re.search('function y\(\) \{return "(.*?)";', all_text)
    return split_chars.group(1)
   
def find_content(all_text):
    counted = {}
    # This should be the most common occourance
    # get the first 3 chars of every line and count them in to a dict
    for line in all_text.split(';'):
        try:
            counted[line[:3]] += 1
        except:
            counted[line[:3]] = 1
    var_name = max(counted.iteritems(), key=operator.itemgetter(1))[0]

    return var_name

if __name__ == "__main__":
    parser = OptionParser(usage= 'usage: %prog inputfile output_file\nRig Exploit Kit Decoder\nBy Kevin Breen @KevTheHermit')
    parser.add_option('-e', '--exploits', action='store_true', default=False, help="Identify Exploits")
    parser.add_option('-t', '--tidy', action='store_true', default=False, help="Tidy the output code")
    (options, args) = parser.parse_args()
    
    # Start here
    if len(args) < 2:
        parser.print_help()
        sys.exit()

    input_file = args[0]
    output_file = args[1]

    print "[+] Reading input file"
    landing_page = open(input_file, 'r').read()

    # Find the split char it always seems to be in y()
    split_char = find_split(landing_page)

    # Find the var that holds the content
    var_name = find_content(landing_page)

    # Remove all Comments
    landing_page = clean_comments(landing_page)

    # Extract all the contents
    coded_line = ""
    for line in landing_page.split(';'):
        if line.startswith(var_name):
            coded_line += line.split('"')[1]

    # Decode Char Codes
    out_string = ""
    char_list = coded_line.split(split_char)
    for char in char_list:
        try:
            out_string += chr(int(char))
        except:
            print "  [-] Failed to read {0}".format(char)

    # remove comments again
    out_string = clean_comments(out_string)

    # Write out to file
    if options.tidy:
            out_string = out_string.replace(';',';\n')
            out_string = out_string.replace('}', '}\n')
    with open(output_file, 'w') as out:
        out.write(out_string)

    print "[+] Output Written to: {0}".format(output_file)
    
    if options.exploits:
        print "Searching for Possible Exploits"
        if 'ShockwaveFlash' in out_string:
            print "  [-] Found Possible Flash Exploit"
        if 'silverlight' in out_string:
            print "  [-] Found Possible SilverLight Exploit"
        if 'gum.dashstyle' in out_string:
            print "  [-] Found Possible Internet Explorer Exploit"    
        if '<applet>' in out_string:
            print "  [-] Found Possible Java Exploit" 
            
            
