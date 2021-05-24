#!/usr/bin/env python3
""" 
The following program contains a Object tracker class. 
It trackes objects in 3d space using colour as the main differentiator.
It requires stereo images as inputs to it can calcualte x,y and Z location of \
all colour objects in those locations.

It currently has the ability to track ['Red','Green','Blue','White','Orange',/
'Cyan',Yellow]. Support for more clours can be added with very little effort.

A Object tracker would require the camera parameters to be defined will creating its object. 
"""
#----------------------------------------
#Importing libraries
#----------------------------------------

import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import math

#-----------------------------------------
#class defintion
#-----------------------------------------

class Object_Tracker():
    """ 
        Object tracker can we used to detect multiple coloured objects from \
        left and right setero RGB images and calculate the distance to the\ 
        object from the camera setup. 
        An instance of the object can be created by passing on the dimensions\ 
        of the images and focal length and distance between the axis of the \
        cameras( Both the focal length and distance b/w axis should be sent in meters)
        
        Eg : Temp_obj_trck = Object_Tracker((256,256,3),10,10,0.001)
        
        Above example creates a instance of an object traker which takes two 256*256 colour\
        images from two identicial cameras which have a focal length of 10 meters and \
        the axis separated by 10m. The pixel spacing of images is 0.001 meters\
        The present colours it support tracking are as follows ["Red", "Grey", /
        "Blue", "Cyan", "Yellow", "Green","Orange"]
        Only RGB colour space images should be passed to Object_Tracker and it returns\
        distnace of all the objects found along witht the objct height from the origin \
        or center of axis of cameras. An example of how distance is reported is shown below.
        distance = {
                    'Red': [600.0],
                    'White': [575.3424657534247, 626.8656716417911, 626.8656716417911],
                    'Blue': [656.25],
                    'Cyan': [567.5675675675676],
                    'Yellow': [656.25],
                    'Green': [575.3424657534247],
                    'Orange': [567.5675675675676]
                   }
                   
    """

    def __init__(self,image_size,focal_length, Dist_Cameras, \
                 pixel_spacing, debug = False):

        self.x_pixel_size    = image_size[1]
        self.y_pixel_size    = image_size[0]
        self.f_length        = focal_length
        self.Axis_separation = Dist_Cameras
        self.pixel_length = pixel_spacing
	# Colour objects it supports tracking
        self.colours = ["Red", "White", "Blue", "Cyan", "Yellow", "Green","Orange"]

        self.colour_ranges = {}

        # Each colour Low and High ranges in HSV colour space
        self.colour_ranges["Red"]  = {
                                     "Low_Range"  : np.array([0,40,40]),
                                     "High_Range" : np.array([10,255,255]),
                                     "Low_Range2" : np.array([170,40,40]),
                                     "High_Range2" : np.array([180,255,255])
                                    }
       # Red has two colour ranges since it wraps around.

        self.colour_ranges["White"] = {
                                     "Low_Range"  : np.array([0,0,25]),
                                     "High_Range" : np.array([0,40,255])
                                     }

        self.colour_ranges["Blue"] = {
                                     "Low_Range"  : np.array([108,40,40]),
                                     "High_Range" : np.array([130,255,255])
                                     }

        self.colour_ranges["Cyan"] = {
                                     "Low_Range"  : np.array([85,40,40]),
                                     "High_Range" : np.array([95,255,255])
                                     }

        self.colour_ranges["Yellow"] = {
                                     "Low_Range"  : np.array([30,40,40]),
                                     "High_Range" : np.array([35,255,255])
                                     }

        self.colour_ranges["Orange"] = {
                                     "Low_Range"  : np.array([11,40,40]),
                                     "High_Range" : np.array([27,255,255])
                                     }

        self.colour_ranges["Green"] = {
                                     "Low_Range"  : np.array([40,40,40]),
                                     "High_Range" : np.array([70,255,255])
                                     }
        if debug ==True:
            self.debug = True
        else:
            self.debug = False
        self.debug_intr = False

    def Distance_calculation(self, Left_centers, Right_centers):
        """     
            Distance_calculation function calculates the distance of an\ 
            object from the cameras 
            
            It accepts the centers of the object(s) found in both the\ 
            left and right camera images of a frame 

            The reported distance is in meters

            if the object is detected only in one of either left or right\ 
            images then distance will not be calcualted for that blob. 

            Additional logic is added for asserting distance is calculated by correctly \
            identifying same blob centers in left and right frames and correct \
            blob center is elminated if uneven no of blob centers are \
            detected in left and right images 
        """
        temp_left_cent= []
        temp_right_cent = []

        if len(Left_centers) != 0:
            for cent in Left_centers:
                #print("Cent ",cent)
                tempx = cent[0] - self.x_pixel_size//2
                tempy = self.y_pixel_size//2 - cent[1]
                temp_left_cent.append([tempx,tempy])

        if len(Right_centers) != 0:
            for cent in Right_centers:
                tempx = cent[0] - self.x_pixel_size//2
                tempy = self.y_pixel_size//2 - cent[1]
                temp_right_cent.append([tempx,tempy])

        temp_left_cent  = np.sort (temp_left_cent, axis = 0)
        temp_right_cent = np.sort (temp_right_cent, axis = 0)

        if self.debug == True:
            print("calculated Left Centers =", temp_left_cent)
            print("calculated Right Centers =", temp_right_cent)

        # if not same of objects are found in left and right images then\ 
        # distance is calculated for the objects present in both images

        if len(Left_centers) != len(Right_centers):            
            valid_obj = min(len(Left_centers), len(Right_centers))

        else:
            valid_obj = len(Left_centers)

        Distance_H = []
        Distance_V = []

        # If more objects are present in left image then objects present \
        # towards left most of the image is dicarded

        if len(Left_centers) > len(Right_centers):
            for i in range(len(Left_centers) - valid_obj):
                np.delete(temp_left_cent,0)

        elif len(Left_centers)< len(Right_centers):
            for i in range(len(Right_centers) - valid_obj):
                np.delete(temp_right_cent,-1)

        if self.debug == True:
            print("calculated Left Centers = ", temp_left_cent)
            print("calculated Right Centers = ", temp_right_cent)

        for i in range(valid_obj):

            assert ((temp_right_cent[i][1]-1)<= temp_left_cent[i][1] <= \
            (temp_right_cent[i][1]+1)), \
            "The vertical hight of the centers considered for distance calculation is not matching"

            if self.debug_intr == True:
                print ("The passed centers are", \
                temp_left_cent[i],temp_right_cent[i])

            calc_H_dist = (self.f_length * self.Axis_separation) / (temp_left_cent[i][0]*\
                           self.pixel_length - temp_right_cent[i][0] * self.pixel_length)

            calc_V_dist = Left_centers[i][0] * self.pixel_length

            Distance_H.append(calc_H_dist)
            Distance_V.append(calc_V_dist)

        if self.debug ==True:
            print("Distance calculated", Distance_H, Distance_V)

        return Distance_H,Distance_V
    
    def blob_detection(self,Org_img , Lower_limit, Upper_limit):

        # Colour thresholding the images
        masked  = cv.inRange(Org_img, Lower_limit, Upper_limit)

        # Contours detection from the thresholded images
        contours, _ = cv.findContours (masked, cv.RETR_EXTERNAL, 
                                         cv.CHAIN_APPROX_SIMPLE)

        return contours
    
    def center_calculation(self,contours):
        """ 
            center_caclulation function takes one input 'countours' for \
            which center is to be calculated.

            If atleas one contour is found for that coloue in the image\ 
            then center of the contour is calculated by findig the \
            momentum of the contours. 

            momentum cannot be calculated if the found contour is less than three\ 
            pixel size in that case the left most pixel is considered as center
        """
        # Temp variables for storing the center position calculated for different contours   
        centers  = []

        if len(contours) != 0:

            if self.debug_intr == True:
                print("contours found", len(contours))

            for cnt in contours:

                if len(cnt) >= 3:
                    M = cv.moments(cnt)
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    centers.append([cx,cy])

                else:
                    centers.append(cnt[0][0])

        if self.debug_intr == True:
            print("Centers:",centers)

        return centers
    
    def object_identification(self, Left_image, Right_image):
        """
            Object identification takes left and right camera images of a frame and\ 
            calculates distances and centers of different colour objects.
            It makes use of center_caclulation,blob_detection,Distance_calculation functions
            it returns the distances and calculated centers for each colour in dictonary
        """
        # Convertign the images from RGB colour space to HSV colour space

        Left_HSV  = cv.cvtColor (Left_image, cv.COLOR_RGB2HSV)
        Right_HSV = cv.cvtColor (Right_image, cv.COLOR_RGB2HSV)

        # empty dictonary varibales for storing the calculated Distances and \
        # Centers for different colour objects

        Distances_H = {}
        Distances_V = {}
        Centers = {}

        for colour in self.colours:
            if self.debug == True:
                print("colour:",colour)

            if colour == "Red":

                left_cont1  = self.blob_detection(Left_HSV, \
                              self.colour_ranges[colour]["Low_Range"],\
                              self.colour_ranges[colour]["High_Range"])

                left_cont2  = self.blob_detection(Left_HSV, \
                              self.colour_ranges[colour]["Low_Range2"],\
                              self.colour_ranges[colour]["High_Range2"])

                right_cont1 = self.blob_detection(Right_HSV, \
                              self.colour_ranges[colour]["Low_Range"],\
                              self.colour_ranges[colour]["High_Range"])

                right_cont2 = self.blob_detection(Right_HSV, \
                              self.colour_ranges[colour]["Low_Range2"],\
                              self.colour_ranges[colour]["High_Range2"])

                left_centers  = self.center_calculation(left_cont1 + left_cont2)
                right_centers = self.center_calculation(right_cont1 + right_cont2)

                Centers[colour] = { 
                                    "Left_cent"  : left_centers,
                                    "Right_cent" : right_centers
                                  }

                distance_H,distance_V = \
                self.Distance_calculation(left_centers , right_centers)

                Distances_H[colour] = distance_H
                Distances_V[colour] = distance_V

            else:

                left_cont  = self.blob_detection(Left_HSV, \
                             self.colour_ranges[colour]["Low_Range"],\
                             self.colour_ranges[colour]["High_Range"])

                right_cont = self.blob_detection(Right_HSV, \
                             self.colour_ranges[colour]["Low_Range"],\
                             self.colour_ranges[colour]["High_Range"])

                left_centers = self.center_calculation(left_cont)
                right_centers = self.center_calculation(right_cont)

                Centers[colour] = { 
                                    "Left_cent"  : left_centers,
                                    "Right_cent" : right_centers
                                  }

                distance_H,distance_V = \
                self.Distance_calculation(left_centers, right_centers)

                Distances_H[colour] = distance_H
                Distances_V[colour] = distance_V

        return Distances_H, Distances_V
#------------------------------------------------
#End of Object Tracker class difinition 
#------------------------------------------------
