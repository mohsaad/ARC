#!/usr/bin/env python2

# Mohammad Saad
# 9/17/2015
# get_map.py
# Grabs a map and overlays the SLAM output
# onto the map.

import numpy as np
import cv2
import requests
import shutil
import math
from math import radians
import utm
import argparse

class MapOverlayer():
	

	# constructor
	# gets gps coordinates and stores them in an array
	def __init__(self, gps_file, api_key):
		self.gps_coords = []
		count = 0
		with open(gps_file, 'r') as f:
			for line in f:
				data_arr = line.split(',')
				if(data_arr[0] == '%INSPVASA'):
					(x,y) = (data_arr[4],data_arr[5])
					self.gps_coords.append((x,y))
					count += 1
		
		f.close()
		
		print count
		print(self.gps_coords[0])
		
		self.api_key = api_key
		self.base_url_1 = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/Aerial/'
		self.base_url_2 = '?mapSize=600,600&key='+api_key
		self.path = '/home/saad/Documents/Research/img.png'


	def find_avg(self, list_of_coords):
		total_x = 0.0
		total_y = 0.0
		for coord in list_of_coords:
			total_x += float(coord[0])
			total_y += float(coord[1])

		return (total_x/len(list_of_coords), total_y/len(list_of_coords)) 

	# gets the image itself
	def get_starting_image(self, zoom_level, size):
		first_coord = self.find_avg(self.gps_coords)
		self.center = first_coord
		self.zoom_lvl = zoom_level

		url = self.base_url_1 + str(first_coord[0])+',' + str(first_coord[1]) + '/' + str(zoom_level)
		url += self.base_url_2
		
		r = requests.get(url)
		


		print first_coord
		print r.status_code

		if r.status_code == 200:
   			 with open(self.path, 'wb') as f:
        			r.raw.decode_content = True
        			shutil.copyfileobj(r.raw, f)


	# reads image in to draw coordinates on
	def get_image(self):
		self.img = cv2.imread('img.png')
		#cv2.imshow('img',self.img)
		#cv2.waitKey(0) # for debugging

	def get_meters_per_pixel(self, zoom_level):
		return (math.cos(self.center[0] *math.pi/180) * 2 * math.pi * 6378137) / (256 * (2 ** zoom_level))

	def find_distance_between_gps(self, gps1, gps2):
		R = 6371
		dLat = radians(float(gps1[0])-float(gps2[0]))
		dLon = radians(float(gps1[1])-float(gps2[1]))
		lat1 = radians(float(gps1[0]))
		lat2 = radians(float(gps2[0]))
		
		a  = math.sin(dLat/2) * math.sin(dLat/2) +  math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2) 	
		
		b = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
		d = R * b
		

		return d*1000

	def find_start_point(self):
		center = self.find_avg(self.gps_coords)
		
		first = self.gps_coords[0]
		
		diffV = abs(self.find_distance_between_gps(center, (center[0],first[1])))
		diffH = abs(self.find_distance_between_gps((first[0],center[1]), center))
		
		totalPixelX = math.floor(diffH / self.get_meters_per_pixel(self.zoom_lvl))
		totalPixelY = math.floor(diffV / self.get_meters_per_pixel(self.zoom_lvl))
		
		[h, w] = self.img.shape[:2]
		self.start = (w/2 - totalPixelX, h/2 - totalPixelY)
		self.img[self.start[1], self.start[0]] = [0,0,255]

			
	def gps_dist_in_pixels(self, gps1, gps2):
		diffV = abs(self.find_distance_between_gps(gps1, (gps1[0],gps2[1])))
                diffH = abs(self.find_distance_between_gps((gps2[0],gps1[1]), gps1))
		if(gps1[0] > gps2[0]):
			diffH *= -1
		
		if(gps1[1] > gps2[1]):
			diffV *= -1

                totalPixelX = diffH / self.get_meters_per_pixel(self.zoom_lvl)
                totalPixelY = diffV / self.get_meters_per_pixel(self.zoom_lvl)

		return (totalPixelX, totalPixelY)


	def plot_gps_data(self, color = [0,0,255]):
		(currX, currY) = self.start
		(lastIntX, lastIntY) = self.start
		for i in range(1, len(self.gps_coords)):
			(tX,tY) = self.gps_dist_in_pixels(self.gps_coords[i], self.gps_coords[i-1])
			currX += tX
			currY += tY
			
			if(currX >= lastIntX + 1):
				lastIntX = math.floor(currX)
			elif(currX <= lastIntX - 1):
				lastIntX = math.ceil(currX)
			else:
				pass

			if(currY >= lastIntY + 1):
				lastIntY = math.floor(currY)
			elif(currY <= lastIntY -1):
				lastIntY = math.ceil(currY)
			else:
				pass

			if(lastIntX < 0):
				break
			elif(lastIntX >= self.img.shape[0]):
				break
			else:
				pass

			if(lastIntY < 0):
				break
			elif(lastIntY >= self.img.shape[1]):
				break
			else:
				pass
			
			self.img[lastIntX][lastIntY] = color
							
					
	def showImg(self):
		cv2.imshow('img',self.img)
                cv2.waitKey(0) # for debugging
		

	def plotResults(self, filename):
		self.gps_coords = []
		with open(filename, 'r') as f:
			count = 0
			for line in f:
				if count == 0:
					count += 1
					continue
				
				line = line.split(",")
				zone = int(line[1])
				east = float(line[3])
				north = float(line[4]) 
				
				self.gps_coords.append(utm.to_latlon(east, north,zone, northern = True))
		f.close()
	
	def load_slam_data(self, filename):
		self.east = []
		self.north = []
		i = 0
		with open(filename, 'r') as f:
                        for line in f:
				if i == 0:
					i = 1
					continue
                                line = line.split(',')
                                self.east.append(float(line[3]))
                                self.north.append(float(line[4]))
                f.close()
			

	def get_second_results(self, color = [255,0,0]):
		
		(currX, currY) = self.start
		(lastIntX, lastIntY) = self.start			
				
		for i in range(1, len(self.north)):
			tX = -1*(self.north[i] - self.north[i - 1])/self.get_meters_per_pixel(self.zoom_lvl)
			tY = (self.east[i] - self.east[i - 1])/self.get_meters_per_pixel(self.zoom_lvl)
			
			currX += tX
                        currY += tY

                        if(currX >= lastIntX + 1):
                                lastIntX = math.floor(currX)
                        elif(currX <= lastIntX - 1):
                                lastIntX = math.ceil(currX)
                        else:
                                pass

                        if(currY >= lastIntY + 1):
                                lastIntY = math.floor(currY)
                        elif(currY <= lastIntY -1):
                                lastIntY = math.ceil(currY)
                        else:
                                pass

                        if(lastIntX < 0):
                                break
                        elif(lastIntX >= self.img.shape[0]):
                                break
                        else:
                                pass

			if(lastIntY < 0):
                                break
                        elif(lastIntY >= self.img.shape[1]):
                                break
                        else:
                                pass

                        self.img[lastIntX][lastIntY] = color				
					
	
	def test(self):
		for i in range(1, 1000):
			print str(self.find_distance_between_gps(self.gps_coords[0], self.gps_coords[1])) + " " + str(i) + " " + str(i-1)	

def main(args):
	
	m = MapOverlayer(args.gps, args.key)
	
	m.get_starting_image(15,0)
	m.get_image()
	
	m.find_start_point()
	m.plot_gps_data()

	m.load_slam_data(args.slam)
	m.find_start_point()
	m.get_second_results()
	m.showImg()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
        parser.add_argument('--gps', help = 'GPS data file')
        parser.add_argument('--slam', help = 'SLAM output')
        parser.add_argument('--key', help = 'Bing Maps API key')
        args = parser.parse_args()
	print args.gps
	main(args)	
