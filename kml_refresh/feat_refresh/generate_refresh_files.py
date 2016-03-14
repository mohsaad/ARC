#!/usr/bin/env python
# Mohammad Saad
# 3/12/2016
# generate_refresh_files.py
# Generates files for KML refresher

import sys

num_files = sys.argv[1]
directory = sys.argv[2]
name = sys.argv[3]

for i in range(0, int(num_files)):
	f = open(directory + '/' + str(i) + name, 'w')
	f.close()
	print directory + '/' + str(i) + name

print "done"
