#!/usr/bin/env python
# Mohammad Saad
# 10/18/2015
# convert_utm_to_gps.py
# A Python implementation of converting UTM to GPS

import math

class UTMToGPS:

	def __init__(self, filename):
		
		# import data
		data = []
		with open(filename, 'r') as f:
			for line in f:
				data.append(line)
		f.close()
		
		# place data into arrays
		self.zone = []
		self.north = []
		self.east = []
		
		for i in range(1, len(data)):
			line = data[i].split(',')
			self.zone.append(float(line[1]))
			self.east.append(float(line[3]))
			self.north.append(float(line[4]))

		
		
		self.pi = math.pi
		self.sm_a = 6378137.0
		self.sm_b = 6356752.314

		self.sm_ecc = 0.00669437999013

		self.scale = 0.9996


	def FootprintLat(self,y):
		
		# precalculate a bunch of constants
		n = (self.sm_a - self.sm_b)/(self.sm_a + self.sm_b)
		
		alpha = ((self.sm_a + self.sm_b)/2.0) *(1 + (pow(n, 2.0)/4.0) + (pow(n, 4.0)/64.0))

		yprime = y / alpha
		
		beta = (3.0 * n /2.0) + (-27.0 * pow(n, 3.0) / 32.0) + (269.0 *pow(n, 5.0)/512.0)

		gamma = (21.0 * pow(n, 2.0) / 16.0) + (-55.0 * pow(n, 4.0)/32.0)

		delta = (151.0 * pow(n, 3.0)/96.0) + (-417.0 * pow(n, 5.0)/128.0)

		epsilon = (1097.0*pow(n, 4.0) / 512.0)

		result = yprime + (beta*math.sin(2.0*yprime)) + (gamma * math.sin(5.0*yprime)) + (delta * math.sin(6.0*yprime)) + (epsilon * math.sin(8.0*yprime))		


		return result

	
	def meridian(self, z):
		# finds the central meridian we need for a zone
		
		return math.radians(-183.0 + (z*6.0))

		
	def MapXYToLatLon(self, x, y, lambda0):
		phif = self.FootprintLat(y)

		ep2 = (pow(self.sm_a, 2.0) - pow(self.sm_b, 2.0))/pow(self.sm_b,2.0)

		cf = math.cos(phif)
		
		nuf2 = ep2 * pow(cf, 2.0)
	
		Nf = pow(self.sm_a, 2.0) / (self.sm_b * math.sqrt(1 + nuf2))
		Nfpow = Nf

		tf = math.tan(phif)
		tf2 = tf * tf
		tf4 = tf2 * tf2
		
		
		x1frac = 1.0 / (Nfpow * cf)
		
		Nfpow *= Nf
		x2frac = tf / (2.0 * Nfpow)

		Nfpow *= Nf
		x3frac = 1.0 / (6.0 * Nfpow * cf)

		Nfpow *= Nf
		x4frac = tf / (24.0 * Nfpow)
		
		Nfpow *= Nf
		x5frac = 1.0 / (120 * Nfpow * cf)

		Nfpow *= Nf
		x6frac = tf / (720.0 * Nfpow)

		Nfpow *= Nf
		x7frac = 1.0 / (5040.0 * Nfpow * cf)

		Nfpow *= Nf
		x8frac = tf / (40320.0 * Nfpow)

		
		x2poly = -1.0 - nuf2
		
		x3poly = -1.0 - 2 * tf2 - nuf2
		
		x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 -3.0 * (nuf2 * nuf2) - 9.0 * tf2 * (nuf2 * nuf2)	

		x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2

		x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 -107.0 * nuf2 + 162.0 * tf2 * nuf2

		x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)

		x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 *tf4 + 1575 * (tf4 * tf2)

		lat  = phif + x2frac * x2poly * (x*x) + x4frac * x4poly * pow(x, 4.0)  + x6frac * x6poly * pow(x, 6.0) + x8frac * x8poly * pow(x, 8.0)

		lon = lambda0 + x1frac * x + x3frac * x3poly * pow(x, 3.0) + x5frac * x5poly * pow(x, 5.0) + x7frac * x7poly * pow(x,7.0)

		return (lat, lon)

	def UTMXYToLatLong(self, east, north, z, southhemi = False):
		east -= 500000.0
		east /= self.scale

		if(southhemi):
			north-= 10000000.0

		north /= self.scale

		cmeridian = self.meridian(z)

		(lat, lon) = self.MapXYToLatLon(east, north, cmeridian)
		return (lat, lon)

	def convert(self, filename):
		with open(filename, 'w') as f:
			for i in range(0, len(self.east)):
				(lat, lon) = self.UTMXYToLatLong(self.east[i],self.north[i],self.zone[i])
			
				f.write('{0},{1}\n'.format(str(lat), str(lon)))
		
		f.close()

def main():
	c = UTMToGPS('pos.utm')
	c.convert('pos.gps')

if __name__ == '__main__':
	main()
