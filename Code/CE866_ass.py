#!/usr/bin/env python3
"""
PURPOSE :
The program is intended to identify UFO object with non linear motion from a\ 
set of stereo images.
 
The no of frames and left and right set of images from different \
frames can be passed to the program from the terminal.

	Eg invoking: python3 ce866ass.py 50 left-%3.3d.png right-%3.3d.png

Here 50 is the frame count and left-%3.3d.png are left images and right-%3.3d.png\ 
is for right camera images. The order should not be altered in any way.
The makes use of two classes "object_finder" & "UFO_finder".
 
Two separate programs are built so that obj_finder can be reused in\ 
other programs where the final operation is different than identifiying a UFO.
 
	1) All the images are read

	2) converted to RGB colour space and passed each left and right image \
           of a frame is passed on to "object_finder" object for identifying \
           different objects and their distances

	3) The calculated distances are then passed on to "UFO_finder"\ 
           for detectign abrupt motion of objects between frames and ufo detection.

The example output of the program is as follows
Frame	Identity	Distance
1 	 Red	1272727272.727 

1 	 White	1312500000.000 1272727272.727 

1 	 Blue	1312500000.000 

1 	 Cyan	1235294117.647 

1 	 Yellow	1312500000.000 

1 	 Green	1235294117.647 

1 	 Orange	1235294117.647 
UFO:	White

if more than one object is found for a similar colour then their distances \
are reported on the same line with a space like white object.
 
if an object is not visible in both or either left or right frames \
then No valid object is printed in place of distance.


@ Author: Chandra Naveen Kumar
Reg no: 2003246   
 """
#--------------------------------------------------------
# Global Variables(camera Parameters)
#--------------------------------------------------------

focal_length = 12
Distance_bw_axis = 3500
pixel_spacing = 0.00001			#All varaibles units are in meters


#---------------------------------------------------------
# Importing required libraries and classes for the program
#---------------------------------------------------------
import sys
import numpy as np
import cv2 as cv
import os
from object_finder import Object_Tracker
from UFO_finder import non_linear_motion_finder

#--------------------------------------------------------
# Variables to enable Debugging of different components
#--------------------------------------------------------
debug = False
debug_obj_det = False
debug_ufo_fin = False

#-------------------------------------------------------
#Reading arguments from termianl
#-------------------------------------------------------
if len(sys.argv) < 4:
	print ("Usage:", sys.argv[0], "<image>...", file=sys.stderr)
	sys.exit(1)

assert int(sys.argv[1]) != 0,\
" PLease provide valid no of frames as first argument to program invoke call"

No_frames = int(sys.argv[1])

if debug == True:	
	print("No of frames provide to program :",No_frames)

# creating empty variables to hold images.
left_frames = []
right_frames = []

# Reading all the images into the program for processing
for frame in range(0,No_frames):

	fn_left = sys.argv[2] % frame
	fn_right = sys.argv[3] % frame

	assert(os.path.isfile(fn_left)), \
        " Following %s file is not present in current directory "%(fn_left)

	assert(os.path.isfile(fn_right)), \
        "Following %s file is not present in current directory "%(fn_right)

	left_frames.append(cv.imread(fn_left))
	right_frames.append(cv.imread(fn_right))

# readng the dimenions of the image.
img_dim = np.shape(left_frames[0])
if debug == True:
	print("Loaded image dimensions: ", img_dim )

# Asserting the read images are colour and not monochrome
assert img_dim[2] == 3, "Please provide colour images for processsing"

# Creating an object for object tracker.
obj_trck = Object_Tracker(img_dim, focal_length, \
Distance_bw_axis, pixel_spacing, debug_obj_det)

# Variables to hold the calcualted horizontal and vertical distances \ 
# of the objects in each frame

cal_distances_H = {}
cal_distances_V = {}

# Creating an non_linraer-motion finder object.
ufo_finder = non_linear_motion_finder(debug_ufo_fin)

print("Frame\tIdentity\tDistance")

# Calculating distances of objects in each frame.
for frame in range(No_frames):

	Left_RGB  = cv.cvtColor (left_frames[frame], cv.COLOR_BGR2RGB)
	Right_RGB = cv.cvtColor (right_frames[frame], cv.COLOR_BGR2RGB)

	temp_distance_H,temp_distance_V = \
        obj_trck.object_identification( Left_RGB, Right_RGB )

	cal_distances_H[frame] = temp_distance_H
	cal_distances_V[frame]   = temp_distance_V

	for colour in temp_distance_H:

		if len(temp_distance_H[colour])  == 0:
			distance = "No valid Obj found"
			print(frame+1,'\t', colour,'\t', distance, end = "\n")
		else:
			distance = temp_distance_H[colour]
			print(frame+1, '\t', colour, end = "\t")

			for i in range(len(temp_distance_H[colour])):
				print('%.3f' %(temp_distance_H[colour][i]), end =" ")

			print("\n")

# Passing the calculated distances to ufo_finder object
suspected_obj = \
ufo_finder.suspected_obj_finder(cal_distances_H,cal_distances_V)

output_holder = []

# Removing the suscript and fidning the colour of the ufo to report.
for i in range(len(suspected_obj)):

	obj = suspected_obj[i][:-1]
	
	if obj not in output_holder:	
		output_holder.append(obj)

print("UFO:",end = "\t")

for i in range(len(output_holder)):

	print(output_holder[i],end = "\t")

print("\n")

#----------------------------------------------
#End of the program
#----------------------------------------------
	

