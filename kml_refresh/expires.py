#!/usr/bin/python

import random
import time

lat = random.random() * 180. - 90.
lon = random.random() * 360. - 180.

now = time.time()
future = time.gmtime(now + 11)
y = future[0]
mo = future[1]
d = future[2]
h = future[3]
mi = future[4]
s = future[5]
iso8601 = '%04d-%02d-%02dT%02d:%02d:%02dZ' % (y,mo,d,h,mi,s)

print 'Content-type: application/vnd.google-earth.kml+xml'
print

print '<?xml version=\"1.0\" encoding=\"UTF-8\"?>'
print '<kml xmlns=\"http://www.opengis.net/kml/2.2\">'

# must be child of <kml>
print '<NetworkLinkControl>'
print '<expires>%s</expires>' % iso8601
print '</NetworkLinkControl>'

print '<Placemark>'
print '<name>placemark expires %s</name>' % iso8601
print '<Point>'
print '<coordinates>%f,%f,0</coordinates>' % (lon,lat)
print '</Point>'
print '</Placemark>'

print '</kml>'