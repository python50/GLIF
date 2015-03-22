#------------------------------------------------------------------------------
# Gerber Writer - A Wrapper for Gerber Writer Core
#------------------------------------------------------------------------------
#
# Author: Jason White
# Licence: GPLv2
#
# a high-ish level gerber RS274X writer
# Takes in the 5 graphical primitives and
# outputs a gerber file in MM mode
# with positive polarity
#
# Apertures are taken care of here.
#
# all coodinates expected to be integer and in micrometers (6 zeros, 1mm=1000000um)
# but thickness and is expected in milimeters, floating point
#
# check out test_gerber_writer() for an example of how to make it work
#

from math import pi, radians, sin, cos

import types
from symbols import *
import group
from primitives import *

from gerber_writer_core import *

class gerber_writer:
	def __init__(self, filename):
		self.filename=filename
		self.f=open(filename, "w")
		self.apertures=[]
		self.primitives=[]
	
	def write(self):
		write_start(self.f)
		
		self.define_apertures()
		
		write_apertures(self.f, self.apertures)
		
		self.write_primitives()
		
		write_end(self.f)
		
	def write_primitives(self):
		for i, p in enumerate(self.primitives):
			self.write_primitive(i, p)
	
	def write_primitive(self, i, p):
		if isinstance(p,line):
			write_line(self.f, p.aperture, [p.start.x, p.start.y], [p.end.x, p.end.y])
		elif isinstance(p,arc):
			self.write_arc(p)
		elif isinstance(p,circle):
			write_line(self.f, p.aperture, [p.location.x, p.location.y], [p.location.x, p.location.y])
		elif isinstance(p,text):
			self.write_text(p)
		elif isinstance(p,polygon):
			write_polygon(self.f, p.location.x, p.location.y, p.points)
		else:
			print("Error unsupported primitive %s" % p)
	
	def rotate_point(self, point, angle, offset=(0.0, 0.0)):
	    angle = radians(angle)
	    
	    delta_x = point[0]
	    delta_y = point[1]
	    
	    x = offset[0] + (cos(angle) * delta_x) - (sin(angle) * delta_y)
	    y = offset[1] + (sin(angle) * delta_x) + (cos(angle) * delta_y)
	    return (x, y)
		
	def write_text(self, p):
		offset=0
		center=(p.location.x,p.location.y)
		
		for char in p.text:
					
			for i in SYMBOLS[char].elements:
				
				start_point=(offset+i.x1*p.height, i.y1*p.height)
				end_point=(offset+i.x2*p.height, i.y2*p.height)
				
				start_location=self.rotate_point(start_point, p.angle, center)
				end_location=self.rotate_point(end_point, p.angle, center)
				
				write_line(self.f, p.aperture, start_location, end_location)
					
			offset+=SYMBOLS[char].size*p.height
			
	def limit_range(self, value, minimum, maximum):
		if value < minimum:
			return minimum
		if value > maximum:
			return maximum
		
		return value
			
	def write_arc(self, p):
		x=p.location.x
		y=p.location.y
		x_scale=self.limit_range(p.x_scale, 0, 1)
		y_scale=self.limit_range(p.y_scale, 0, 1)
		
		start_angle=self.limit_range(p.angular_dimesions.x, 0 ,360)
		end_angle=self.limit_range(p.angular_dimesions.y, 0, 360)
		
		if start_angle>end_angle:
			temp=start_angle
			start_angle=end_angle
			end_angle=start_angle
		
		delta=end_angle-start_angle
		radius=p.radius
		
		#radius is in micrometers
		length=(delta/360.0)*(2*pi*radius*0.000001)
		
		#One segment for every 0.1mm
		segments=int(round(length*10)+1)

		#compute delta per segment
		delta/=float(segments)
		
		current_angle=float(start_angle)
		for i in range(segments):
			x1=x+round(x_scale*cos(radians(current_angle))*radius)
			y1=y+round(y_scale*sin(radians(current_angle))*radius)
			
			current_angle+=delta
			
			x2=x+round(x_scale*cos(radians(current_angle))*radius)
			y2=y+round(y_scale*sin(radians(current_angle))*radius)
			
			
			write_line(self.f, p.aperture, (x1, y1), (x2, y2))
		
			
		
	def define_apertures(self):
		for i, p in enumerate(self.primitives):
			self.define_aperture(i, p)
				
	def define_aperture(self, i, p):
		#All other types (line, arc, circle, text) use custom width apertures
		if isinstance(p, polygon):
			return
			
		
		a=aperture("C", p.design_rules.thickness)
		if isinstance(p, line):
			a.type=p.shape
		
		p.aperture=self.check_duplicate(a)
		
		if type(p.aperture)!=int:
			p.aperture=len(self.apertures)
			self.apertures.append(a)
			
		
		
	def check_duplicate(self, aperture):
		for i, a in enumerate(self.apertures):
		
			if a.type==aperture.type and a.size==aperture.size:
				return i
		return False
		

def test_gerber_writer():	
	writer=gerber_writer("export2.gbr")
	
	writer.primitives=[
		arc( -2000000, 0, 500000, "C", 1, 1, 270, 315, 0, "", thickness=0.1, clearance=None),
		arc( -2000000, 0, 500000, "C", 1, 1, 135, 225, 0, "", thickness=0.1, clearance=None),
		arc( -2000000, 0, 500000, "C", 1, 1, 0, 90, 0, "", thickness=0.1, clearance=None),
		arc( -2000000, 1000000, 1000000, "C" ,0.5, 1, 0, 180, 0, "", thickness=0.1, clearance=None),
		arc( -2000000, 1000000, 1000000, "C", 0.3, 0.6, 0, 180, 0, "", thickness=0.1, clearance=None),
		
		arc( -2000000, 3500000, 1000000, "C", 1, 0.75, 30, 330, 0, "", thickness=0.1, clearance=None),
		arc( -2000000, 3500000, 1000000, "C", 0.66, 0.5, 30, 330, 0, "", thickness=0.1, clearance=None),
		line(1000000, 1000000, 2000000, 2000000, "C", 0, "copper", thickness=0.25, clearance=None),
		line(1000000, 2000000, 2000000, 3000000, "R", 0, "copper", thickness=0.5, clearance=None),
		line(1000000, 3500000, 2000000, 3500000, "C", 0, "copper", thickness=0.25, clearance=None),

		line(1000000, 4000000, 2000000, 4000000, "R", 0, "copper", thickness=0.25, clearance=None),
		line(2500000, 1000000, 2500000, 1000000, "R", 0, "copper", thickness=1, clearance=None),

		circle(0000000, 0000000, 0, "copper", thickness=0.5, clearance=None),
		circle(0000000, 2000000, 0, "copper", thickness=0.5, clearance=None),
		circle(3500000, 3000000, 0, "copper", thickness=1.25, clearance=None),


		polygon(1000000, 0, 1, [(3000000,0),(4000000,0),(4000000,1500000),  (2500000,1500000), (3000000,1000000)], 0, "copper", thickness=0.0, clearance=None),
		text(0, -1500000, "Hello", 1, 0, 0, "copper", thickness=0.075, clearance=None),
		text(0, -3500000, "There!", 2, 0, 0, "copper", thickness=0.15, clearance=None),
		text(6000000, -1000000, "Any Angle Text", 0.5, 45, 0, "copper", thickness=0.04, clearance=None)
	]
	
	writer.write()
		
test_gerber_writer()
