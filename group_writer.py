from math import pi, radians, sin, cos
import gerber_writer as gerber
from group import *
from primitives import *

"""
	The purpose of group_writer.py is to "digest" a list of groups and primtives
	into a single massive list of primtives located at their final coordinates
	so that they may be written out by gerber_writer.py
	
	The following actions are applied to groups:
		- A toplevel group is selected and interated through
		- The most deeply nested group is selected
		- Each group or primitive contained is rotated by the group's angle and copied to the group one layer above
		- This is repeated for each of the lowest groups until there are no more groups
		- What results is a list of pimitives in their final coordinates.
"""

class group_writer:
	
	def __init__(self, filename, primitives=[]):
		self.filename=filename
		self.primitives=primitives
		
	def rotate_point(self, point, angle, offset=(0.0, 0.0)):
	    angle = radians(angle)
	    
	    delta_x = point[0]
	    delta_y = point[1]
	    
	    x = offset[0] + (cos(angle) * delta_x) - (sin(angle) * delta_y)
	    y = offset[1] + (sin(angle) * delta_x) + (cos(angle) * delta_y)
	    return (x, y)
		
	def rotate_primitive(self, p, angle, offset):
		if isinstance(p, line):
			
			start=(p.start.x, p.start.y)
			end=(p.end.x, p.end.y)
			
			p.start.x, p.start.y = self.rotate_point(start, angle, offset)
			p.end.x, p.end.y = self.rotate_point(end, angle, offset)	
		else: #arc, circle, polygon, and text
			point=(p.location.x, p.location.y)
			p.location.x, p.location.y = self.rotate_point(point, angle, offset)
			
		if isinstance(p, text):
			p.angle+=angle
			
		elif isinstance(p, polygon):
		
			points=[]
			for i in p.points:
				points.append(self.rotate_point(i, angle))
				
			p.points=points
			
		elif isinstance(p, arc):
			p.angular_dimesions.x+=angle
			p.angular_dimesions.y+=angle
		
		return p
		
	def recursive_group_finder(self, g):
		uplevel=[] #the rotated primitives to be returned to the group above
		
		if isinstance(g, group):
			angle=g.angle
			offset=(g.location.x, g.location.y)
		else:
			angle=0
			offset=(0,0)
		
		for i in g:
			
			if isinstance(i, group):
				i.angle+=angle
				
				
				
				i.location.x, i.location.y=self.rotate_point( (i.location.x, i.location.y), angle, offset)
				
				
				#add the contents of the group below to uplevel
				adding=self.recursive_group_finder(i)
				
				uplevel+=adding
			else:
				p=self.rotate_primitive(i, angle, offset)
				uplevel.append(p) #add p to uplevel
				
		
		return uplevel
				
		
	def process_primitives(self):
		result=self.recursive_group_finder(self.primitives)
		
		return result
		
	def write(self):
		result=self.process_primitives()
		
		writer=gerber.gerber_writer(self.filename, primitives=result)
		writer.write()
			



def test_group_writer():
	small=1000000
	test_group_primitives = [
		line(0, small*2, 0, -small, "C", 0, "copper", thickness=0.25, clearance=None),
		circle(small, 0, 0, "copper", thickness=0.25, clearance=None),
		text(0, -small*2, "Group", 0.75, 0, 0, "copper", thickness=0.05, clearance=None),
		polygon(-small, 0, 0, [(-small,-small/2),(-small,small/2),(small,0)], 0, "copper", thickness=0.0, clearance=None),
		arc(small, 0, small, "S", 1, 1, 45, 315, 0, "copper", thickness=0.25, clearance=None)
	]
	

	dist=10000000
	test_primitives = [
		group(       0,        0, 0, test_group_primitives, angle=0),
		
		group( dist,  0, 0, test_group_primitives, angle=0),
		group( dist,  dist, 0, test_group_primitives, angle=45),
		group( 0, dist, 0, test_group_primitives, angle=90),
		
		group(-dist, dist, 0, test_group_primitives, angle=135),
		group(-dist, 0, 0, test_group_primitives, angle=180),
		group(-dist, -dist, 0, test_group_primitives, angle=215),
		
		group( 0, -dist, 0, test_group_primitives, angle=270),
		group( dist, -dist, 0, test_group_primitives, angle=315),
		
	]
	
	large=60000000
	#Groups containing groups
	offset_primitives = [
		group(large, 0,  0, test_primitives, angle=22.4)
	]
	
	final_primitives = [
		#center
		group(-large, 0, 0, offset_primitives, angle=0),
		
		group(0, 0, 0, offset_primitives, angle=0),
		group(0, 0, 0, offset_primitives, angle=45),
		group(0, 0, 0, offset_primitives, angle=90),
		
		group(0, 0, 0, offset_primitives, angle=135),
		group(0, 0, 0, offset_primitives, angle=180),
		group(0, 0, 0, offset_primitives, angle=215),
		
		group(0, 0, 0, offset_primitives, angle=270),
		group(0, 0, 0, offset_primitives, angle=315),
	]
	
	writer=group_writer("group_export.gbr", final_primitives)
	writer.write()

	return

test_group_writer()
