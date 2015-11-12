#!/usr/bin/env python
# Mohammad Saad
# print_real_time.py
# 11/11/2015
# Prints out data to stdout 
# for testing of mapping

import sys

filename = sys.argv[1]

with open(filename, 'r') as f:
	for line in f:
		print line,
f.close()