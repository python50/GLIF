import pcb_tools as pcb
import pcb_tools.primitives as pcb_primitive
import primitives as glif
import gerber_writer

#hard coded scale for a board in inches
CORD_SCALE=25400000
SCALE=25.4

def convert_to_glif(primitive):
	if isinstance(primitive, pcb_primitive.Line):
		return pcb_line(primitive)
	
	#elif isinstance(primitive, pcb_primitive.Arc):
	#	print "Arc!"
	
	elif isinstance(primitive, pcb_primitive.Circle):
		return pcb_circle(primitive)
		
	elif isinstance(primitive, pcb_primitive.Region):
		return pcb_polygon(primitive)
		
	else:
		print "Unsupported gerber primitive %s " % str(type(pcb_primitive))
	

def pcb_line(p):
	#FIXME! This function does not know what units the gerber uses
	#It assumes millimeters.
	
	new=glif.line(0, 0, 0, 0, "", 0, "")
	
	if isinstance(p.aperture, pcb_primitive.Rectangle):
		new.shape="R"
		new.design_rules.thickness=SCALE*max(p.aperture.width, p.aperture.height)
	else:
		new.shape="C"
		try:
			new.design_rules.thickness=SCALE*p.aperture.diameter
		except:
			new.design_rules.thickness=0.1 #0.1mm default
			print "Error unsupported line shape %s " % str(type(p.aperture))
			
	
	new.start=glif.coordinate(p.start[0]*CORD_SCALE, p.start[1]*CORD_SCALE)
	new.end=glif.coordinate(p.end[0]*CORD_SCALE, p.end[1]*CORD_SCALE)
	
	return new
	
	
def pcb_circle(p):
	#FIXME! This function does not know what units the gerber uses
	#It assumes millimeters.
	
	new=glif.circle(0, 0, 0, 0, "")
	
	new.design_rules.thickness=SCALE*p.diameter		
	
	new.location=glif.coordinate(p.position[0]*CORD_SCALE, p.position[1]*CORD_SCALE)
	
	return new
	
def pcb_polygon(p):
	#FIXME! This function does not know what units the gerber uses
	#It assumes millimeters.
	
	new=glif.polygon(0, 0, 1, [], 0, "")		
	
	for x, y in p.points:
		new.points+=[(x*CORD_SCALE,y*CORD_SCALE)]#[glif.coordinate(x*CORD_SCALE,y*CORD_SCALE)]
	
	return new

primitives=[]

# Read gerber
example = pcb.read('example.gbr')

for i in example.primitives:
	primitive=convert_to_glif(i)
	
	if primitive:
		primitives+=[primitive]
		
print primitives

g=gerber_writer.gerber_writer("pcb_tools_export.gbr")

g.primitives+=primitives
g.primitives+=[glif.text(0,-1*CORD_SCALE, "Imported into GLIF and modified!", 1, 22.5, 0, "", 0.1)]

g.write()


