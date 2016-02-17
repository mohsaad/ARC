#!/usr/bin/python
# Mohammad Saad
# 12/10/2015

import random
import time
import xml.etree.ElementTree as ET
from copy import deepcopy

class MapRefresher:



	def __init__(self, file_to_read, file_to_save):
		self.input = file_to_read
		self.output = file_to_save

		self.dom = ET.parse(self.input)
		self.root = self.dom.getroot()
		self.namespace = '{http://www.opengis.net/kml/2.2}'
		self.names = {}

		# create copy
		self.outroot = ET.fromstring('<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2"></kml>')
		self.outtree = ET.ElementTree(self.outroot)
		self.doc2 = ET.SubElement(self.outroot, 'Document')
		
		# copy over style elements
		self.document = self.root.findall(self.namespace+'Document')[0]
		for child in self.document:
			if child.tag != append_gis_str('Folder'):
				temp = deepcopy(child)
				self.doc2.append(temp)


	'''

	'''
	def write_start_file(self):
		self.outtree.write(self.output)

	def write_header_file(self):
		folder_top = self.document.findall(append_gis_str('Folder'))[0]
		folder_top_2 = ET.SubElement(self.doc2, append_gis_str('Folder'))
		for child in folder_top:
			if child.tag != append_gis_str('Folder'):
				temp = deepcopy(child)
				folder_top_2.append(temp)

		# create mid-level folder
		folder_middle = folder_top.findall(append_gis_str('Folder'))[0]
		folder_middle_2 = ET.SubElement(folder_top_2, append_gis_str('Folder'))
		self.outtree.write("header.kml")


	def write_to_output_kml_interval(self, interval_length = 10):
		print "Place file into google earth"
		# create top-level folder for placemarks
		folder_top = self.document.findall(append_gis_str('Folder'))[0]
		folder_top_2 = ET.SubElement(self.doc2, append_gis_str('Folder'))
		for child in folder_top:
			if child.tag != append_gis_str('Folder'):
				temp = deepcopy(child)
				folder_top_2.append(temp)

		# create mid-level folder
		folder_middle = folder_top.findall(append_gis_str('Folder'))[0]
		folder_middle_2 = ET.SubElement(folder_top_2, append_gis_str('Folder'))

		for child in folder_middle:
			if child.tag != append_gis_str('Folder') and child.tag != append_gis_str('Placemark'):
				temp = deepcopy(child)
				folder_middle_2.append(temp)

		# get array of coordinates for line drawing
		coord_array = []
		line_placemarks = folder_middle.findall(append_gis_str('Placemark'))[0]
		line_placemarks_2 = ET.SubElement(folder_middle_2, append_gis_str('Placemark'))
		line_string = ET.SubElement(line_placemarks_2, append_gis_str('LineString'))
		for child in line_placemarks:
			if child.tag != append_gis_str('LineString'):
				temp = deepcopy(child)
				line_placemarks_2.append(temp)
			else:
				for child2 in child:
					if child2.tag != append_gis_str('coordinates'):
						temp = deepcopy(child2)
						line_string.append(temp)
					else:
						coord_array = child2.text.split('\n')
						coord_array = filter(None, coord_array)
				
				coordinates = ET.SubElement(line_string, append_gis_str('coordinates'))
				coordinates.text = "" # set for updating later

		# get final folder before actual placemarks
		placemark_array = []
		folder_placemark = folder_middle.findall(append_gis_str('Folder'))[0]
		folder_placemark_2 = ET.SubElement(folder_middle_2, append_gis_str('Folder'))
		for child in folder_placemark:
			if child.tag != append_gis_str('Placemark'):
				temp = deepcopy(child)
				folder_placemark_2.append(temp)
			else:
				temp = deepcopy(child)
				placemark_array.append(temp)


		# now... write to output file, delay by interval
		for i in range(0,len(placemark_array)):
			# write placemarks
			folder_placemark_2.append(placemark_array[i])
			# write line drawing
			coordinates.text += coord_array[i]+'\n'
			self.outtree.write(self.output)
			time.sleep(interval_length)	
		
		self.outtree.write(self.output)




'''
append_gis_str
Used to append the xml namespace so we can access elements
'''
def append_gis_str(string):
	return '{http://www.opengis.net/kml/2.2}'+ string


def main():
	m = MapRefresher('pos2.kml', 'output.kml')
	m.write_start_file()
	m.write_header_file()
	# m.write_to_output_kml_interval(0.2)

if __name__ == '__main__':
	main()



