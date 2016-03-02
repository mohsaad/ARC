import os
import random
import xml.etree.ElementTree as ET
import utm
from multiprocessing import Process, Pipe
import time

class RealTimePlotter:

	def __init__(self, header_file, output_file):

		self.header = header_file
		self.curr_index = 0
		self.orig_output_file = output_file
		self.output_file = str(self.curr_index) + output_file 

		self.feat_dict = {}

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

	def reload_file(self):
		self.curr_index += 1
		self.output_file =str(self.curr_index) + self.orig_output_file

		self.feat_dict = {}

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


	def create_point_placemark(self, coords):
		# add to points folder
		pmark = ET.SubElement(self.actual_points, append_gis_str('Placemark'))
			
		styleurl = ET.SubElement(pmark, append_gis_str('styleUrl'))
		styleurl.text = "#track"

		lookat = ET.SubElement(pmark, append_gis_str('LookAt'))
		lat = ET.SubElement(lookat, append_gis_str('latitude'))
		lat.text = str(coords[0])

		longc = ET.SubElement(lookat, append_gis_str('longitude'))
		longc.text = str(coords[1])

		point = ET.SubElement(pmark, append_gis_str('Point'))
		coordtag = ET.SubElement(point, append_gis_str('coordinates'))
		coordtag.text = '{0},{1}'.format(coords[1], coords[0])


	def plot_threaded(self, conn):
		dom = conn.recv()
		dom.write(self.output_file)

	def create_feature_placemark(self, coords, count):
		# add to points folder

		if count in self.feat_dict:
			self.feat_dict[count][0].text = str(coords[0])
			self.feat_dict[count][1].text = str(coords[1])
			self.feat_dict[count][2].text = '{0},{1}'.format(coords[1], coords[0])
			return

		pmark = ET.SubElement(self.actual_points, append_gis_str('Placemark'))
			
		styleurl = ET.SubElement(pmark, append_gis_str('styleUrl'))
		styleurl.text = "#feats"

		lookat = ET.SubElement(pmark, append_gis_str('LookAt'))
		lat = ET.SubElement(lookat, append_gis_str('latitude'))
		lat.text = str(coords[0])

		longc = ET.SubElement(lookat, append_gis_str('longitude'))
		longc.text = str(coords[1])

		point = ET.SubElement(pmark, append_gis_str('Point'))
		coordtag = ET.SubElement(point, append_gis_str('coordinates'))
		coordtag.text = '{0},{1}'.format(coords[1], coords[0])

		self.feat_dict[count] = (lat, longc, coordtag)


	def read_and_write_to_output(self, zone):
		
		# loop
		total_count = 0
		count = 0
		line = ''
		while line is not "END":
			line = raw_input()
			
			# if line is end, stop
			if line == "END":
				print "End of Stream"
				break

			# split up line
			line_arr = line.split(',')
			

			try:
				# plot actual path 
				if len(line_arr) == 10:
					lat = float(line_arr[2])
					lon = float(line_arr[1])
					coords = utm.to_latlon(lat, lon, zone, 'T')
					self.create_point_placemark(coords)
				# plot features
				elif len(line_arr) == 4:
					lat = float(line_arr[2])
					lon = float(line_arr[1])
					if lat > 1000000.0 or lon > 10000000.0:
						continue
					count = int(line_arr[0])
					# convert to latlon
					coords = utm.to_latlon(lat, lon, zone, 'T')
					self.create_feature_placemark(coords, count)

				# otherwise continue
				else:
					pass
			except:
				continue


			# write to file every 100 samples
			if line_arr[0] == '\r':
				total_count += 1
				if total_count % 2== 0:
					t0 = time.time()
					parent_conn, child_conn = Pipe()
					p = Process(target=self.plot_threaded, args=(child_conn,))
					p.start()
					parent_conn.send(self.dom)
					p.join()
					if time.time() - t0 > 0.05:
						self.reload_file()
						print self.curr_index
					print total_count


def append_gis_str(string):
	return '{http://www.opengis.net/kml/2.2}'+ string


def main():
	rtp = RealTimePlotter('header.kml', 'real_time_output.kml')
	rtp.read_and_write_to_output(16)

if __name__ == '__main__':
	main()