#!/usr/bin/env python3
""" 
The program contains non linear motion finder class which can be used to \
detect ufo's based on its trajectory of motion.
 
The objects which are actually travelling in a straight line in 3d will not \
look that when captured in 2d images over a series of frames.
 
They appear to travel in with an inclination from the camera view point.
 
By calulating the angles if makes with the images axis and comparing them\ 
we can determine whether are actually travelling in straight lines or not.
"""

#-----------------------------------------------
# Importing libraries
#-----------------------------------------------
import numpy as np
import math
import os

#----------------------------------------------
#Class definition
#----------------------------------------------

class non_linear_motion_finder():
	""" 
	non_linear_motion_finder can be used to detect which objects are not moving \
        in an straight line, The fucntion takes horizontal distance from the camera \
        and distance wrt to x axis in from the origin to calculate the angle the \
        object is making with the boundaries.
 
        The objects traveling in a stright line in 3 dimensions will have an either \
        incremental or decremental angle pattern based on their direction of motion. 
        Where UFO objects having abrupt motion will have varying angle pattern. 
        It supports tracking of 10 similar colour objects and any no of different\ 
        colour objects
	"""

	def __init__(self,debug= True):

		self.object_angles_per_frame   = {}
		self.max_obj = 10

		if debug == True:
			self.debug = True

		else:
			self.debug = False

	def suspected_obj_finder(self,distances_H:dict,distances_V:dict):

		""" 
		    The function accepts the horizontal distnace and vertical distance and calculates\ 
                    angles made and looks for abrupt movements and returns the suspected obj as list\
		    Eg output: ['Grey0', 'Grey1']		
		"""

		# Calculating angles of all the objects in each frame.

		for frame in range(len(distances_H)):

			angles = self.angle_calculation(distances_H[frame],\
                                 distances_V[frame])

			self.object_angles_per_frame[frame] = angles

		#Creating a temprary object to hold 
                #the angle of an object in a list as a sequence of frames.
		
		temp_holder = {}

		for colour in self.object_angles_per_frame[0]:

			for i in range(self.max_obj):
				temp_holder[colour+str(i)] = []

		# Angle calcualtion, if no of objects detected per each colour is less than max\ 
                # objects then value '0' is appended in that case for ease of computation later.

		# For frames where angles calculation is not poosible also '0' is appended
		for frame in self.object_angles_per_frame:

			for colour in self.object_angles_per_frame[frame]:

				for i in range(self.max_obj):

					if i < len(self.object_angles_per_frame[frame][colour]):

						temp_holder[colour+str(i)].append(\
                                                self.object_angles_per_frame[frame][colour][i])

					else:
						temp_holder[colour+str(i)].append(0)

		if self.debug == True:
			print("Calculated angles",temp_holder)

		UFO = []

		# Verifying straight line motion by comparing angles between frames.
		for obj in temp_holder:

			counter = 0

			for i in range(len(temp_holder[obj])-1):

				if temp_holder[obj][i] == 0 or temp_holder[obj][i] == np.NAN:
					counter+=1 

				elif temp_holder[obj][i] > temp_holder[obj][i+1]:
					counter+=1

				else: 
					counter-=1
			# Objects which traveld in a straight line will have an counter value almost\ 
                        # equal to positive or nrgative frame count.

			# An offset of 3 is being considered to account for start and end frames where\
                        # objects are not visible in both frames for distance and angle calculations.\ 
                        # Also for objects masked by ufos in some frames.

			if self.debug == True:
				print(obj,counter,len(temp_holder[obj]))
			if ((len(temp_holder[obj])-3) <= counter <= (len(temp_holder[obj]))) or \
                        ((len(temp_holder[obj])-3) <= (-1*counter) <= (len(temp_holder[obj]))):

				continue

			else:
				UFO.append(obj)

		if self.debug == True:
			print("Suspected objects",UFO)
		return UFO

	def angle_calculation(self,distance_H : dict,distance_V: dict):

		""" 
                    Angle calculation takes distances of objects of one frame at a time and calculates\ 
                    the angles of the objects with respect to image axis. 
                """
		angles = {}				
		for colour in distance_H:

			# Angles can only be calculated when horizontal distance is availabel.\ 
                        # if it is not present for a frame then NAN is attached to that frame.
 
			if len(distance_H[colour]) != 0:
				temp_ang = []

				for i in range(len(distance_H[colour])):

					ang = math.atan2(distance_V[colour][i],distance_H[colour][i])
					temp_ang.append(ang)
				
				angles[colour] = temp_ang

			else:
				angles[colour] = [np.NAN]

		return angles
						 
	
