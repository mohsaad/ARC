#!/usr/bin/env python
# Mohammad Saad
# print_real_time.py
# 11/11/2015
# Prints out data to stdout 
# for testing of mapping

import sys
import time

filename = sys.argv[1]

with open(filename, 'r') as f:
	for line in f:
		print line,
		time.sleep(0.005)
f.close()