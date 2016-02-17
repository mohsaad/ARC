#!/usr/bin/env python
# Mohammad Saad
# 2/3/2016
# Plots points on KML in
# Real time

import os
import random
import xml.etree.ElementTree as ET
import utm

class RealTimePlotter:

	def __init__(self, header_file, output_file):

		self.header = header_file
		self.output_file = output_file

		self.dom =ET.parse(self.header)
		self.root = self.dom.getroot()

		self.document = self.root.findall(append_gis_str('Document'))[0]

		folder_top = self.document.findall(append_gis_str('Folder'))[0]
		folder = folder_top.findall(append_gis_str('Folder'))[0]

		self.actual_points = ET.SubElement(folder, append_gis_str('Folder'))
		name_points = ET.SubElement(self.actual_points, append_gis_str('Name'))
		name_points.text = "Points"

		line_placemarks = ET.SubElement(folder, append_gis_str('Placemark'))
		name = ET.SubElement(line_placemarks, append_gis_str('Name'))
		name.text = "Path"

		style_url = ET.SubElement(line_placemarks, append_gis_str('styleUrl'))
		style_url.text = '#lineStyle'

		line_string = ET.SubElement(line_placemarks, append_gis_str('lineString'))

		tesselate = ET.SubElement(line_string, append_gis_str('tessellate'))
		tesselate.text = "1"

		self.coordinates = ET.SubElement(line_string, append_gis_str('coordinates'))
		self.coordinates.text = ''
		# test
		self.dom.write(self.output_file)


	def read_and_write_to_output(self):
		# loop
		line = ''
		while line is not "END":
			line = raw_input()
			if line == "END":
				print "End of Stream"
				break

			line_arr = line.split(',')
			
			# continue if first line
			if len(line_arr) is not 6:
				continue

			# convert to latlon
			coords = utm.to_latlon(int(line_arr[3]), int(line_arr[4]), int(line_arr[1]), line_arr[2])

			# add to points folder
			pmark = ET.SubElement(self.actual_points, append_gis_str('Placemark'))
			
			styleurl = ET.SubElement(pmark, append_gis_str('styleUrl'))
			styleurl.text = "#track"

			lookat = ET.SubElement(pmark, append_gis_str('LookAt'))
			lat = ET.SubElement(lookat, append_gis_str('latitude'))
			lat.text = str(coords[0])

			longc = ET.SubElement(lookat, append_gis_str('longitude'))
			longc.text = str(coords[1])

			tilt = ET.SubElement(lookat, append_gis_str('tilt'))
			tilt.text = "66"

			point = ET.SubElement(pmark, append_gis_str('Point'))
			coordtag = ET.SubElement(point, append_gis_str('coordinates'))
			coordtag.text = '{0},{1}'.format(coords[1], coords[0])

			self.coordinates.text += '{0},{1}\n'.format(coords[1], coords[0])

			# write to file every 100 samples
			if int(line_arr[0]) % 100 == 0:
				self.dom.write(self.output_file)

			print line_arr[0]


def append_gis_str(string):
	return '{http://www.opengis.net/kml/2.2}'+ string


def main():
	rtp = RealTimePlotter('header.kml', 'real_time_output.kml')
	rtp.read_and_write_to_output()

if __name__ == '__main__':
	main()