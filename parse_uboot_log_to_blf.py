#! /usr/bin/python
#Load neccessary modules
import sys
import os
import re
import string

if len(sys.argv) != 3:
	print "Usage: ./parse_uboot_log_to_blf.py [uboot_log_name] [blf_file_name]"
	exit(0)

log_name = sys.argv[1]
blf_name = sys.argv[2]

uboot_fp = open(log_name, 'r')
blf_fp = open(blf_name, 'w')

# Read uboot log
uboot_log = uboot_fp.read()

# Define regular expression
content_list = re.findall(r'(\s+(\w+).*==>.*)', uboot_log)

length = len(content_list)
i = 0
while i < length:
	newline = 'PP_WRITE = <' + '0x' + content_list[i][1] + ',' + '0x' + content_list[i+1][1] + ',' + '0x' + content_list[i+2][1] + '>' + '\n'
	blf_fp.writelines(newline)
	i += 3

uboot_fp.close()
blf_fp.close()
