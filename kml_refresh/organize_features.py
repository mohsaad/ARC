#!/usr/bin/env python
# Mohammad Saad
# 1/24/2016
# organize_features.py
# Organizes the features and places them into 
# a gpsbabel-enabled file

class FeatureOrganizer:

	def __init__(self, filename, output):
		self.filename = filename
		self.fpoint = open(self.filename, 'r')
		self.output = output

	def read_features_and_select(self, num_to_skip, zone, ch):
		total_count = 0
		count = 0
		outf = open(self.output, 'w')
		outf.write("No,UTM-Zone,UTM-Ch,UTM-East,UTM-North\n") # place in top for reference
		with self.fpoint as f:
			for line in f:
				line = line.split(',')
				if len(line) == 1:
					count += 1
				if count % num_to_skip == 0:
					if len(line) != 4:
						continue
					else:
						total_count += 1
						outf.write("{0},{1},{2},{3},{4},{5}\n".format(total_count, zone, ch, line[2], line[1], line[0]))

		f.close()
		outf.close()



def main():
	fo = FeatureOrganizer('feats.out', 'out.utm')
	fo.read_features_and_select(30, 16, "T")

if __name__ == '__main__':
	main()