What is GLIF?
========================
GLIF is a Gerber writer written in python. It takes graphical primitives such as lines, arcs, circles, polygons, and ASCII text and writes out valid RS-274X "Gerber" files. These files are typically used to manufacture PCBs.

Features
------------------------
 * Working Gerber import and export (import needs work to add support for few more primitives such as Arcs)

Gerber import
------------------------
 * A working example of using the excellent `pcb-tools` library imports a Gerber (`example.gbr`) as a list of primitives is provided in `pcb_tools_import.py`. After it has been read in modification of the design is easy; the board is then written out as a standard Gerber again (`pcb_tools_export.gbr`).

Gerber export
------------------------
 1. (TODO) Groups and primitives are read from a file. This is either a standard Gerber file, a primitive initialization list, or both. 
 2. (TODO) Groups are rotated and flattened into a list of primitives
 3. This is fed to `gerber_writer.py` which takes the five primitives (`line`, `arc`, `polygon`, `circle`, `text`) and writes them into a standard Gerber RS-274X file with the aid of `gerber_writer_core.py`
 
 Issues
 -----------------------
  1. The units used inside of GLIF are closely tied to the units written out by `gerber_writer.py`. Support needs to be added to convert units on the fly.
