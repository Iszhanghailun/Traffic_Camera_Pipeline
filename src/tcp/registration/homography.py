import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import pickle
import skimage.transform
import cv2


import IPython



class Homography():

    def __init__(self,config):

        '''
        Initilization for Regristration Class 

        Parameters
        -------------
        config: Config
        configuration class for traffic intersection 

        '''

        self.config = config

        # Four corners of the interection, hard-coded in camera space
        self.corners = self.config.street_corners
        # Four corners of the intersection, hard-coded in transformed space
        self.st_corners = self.config.simulator_corners

        #Computes the projected transform for the going from camera to simulator coordinate frame
        self.tf_mat = skimage.transform.ProjectiveTransform()
        self.tf_mat.estimate(self.st_corners, self.corners)


    def determine_lane(self,point):
        '''
        Detemines the lane the current trajectory is on 
        both the index of the lane and the side of the road

        Parameters
        --------------
        point: np.array([x,y])
            The current pose of the car in x,y space

        Returns
        -------------
        dict, containing the current index and road side

        '''

        for i in range(len(self.config.lanes)): 

            lane = self.config.lanes[i]

            if lane.contains_point(point):
                side = lane.side_of_road(point)
                return {'lane_index':i, 'road_side':side}

            
        return None

    def transform_trajectory(self,trajectory):

        '''
        Takes in a trajectory class and converts it to the simulator's frame of reference
        additionally identifies the current lanes

        Parameters
        ---------------
        trajectories: a list of tuple frames
        A list of frames, which is a list state tuples for each timestep

        Returns
        ---------------
        A list of frames, which is a list state dictionaries for each timestep
        '''



        tf_traj = []
        for frame in trajectory:

            new_frame = []

            for obj in frame:

                x,y,cls_label,t,initial_state = obj

                x, y = self.config.alberta_img_dim[0] * x, self.config.alberta_img_dim[1]* y

                tx, ty = self.tf_mat.inverse(np.array((x, y)))[0]
                
                pose = np.array([tx,ty])

                new_obj = {'pose':pose,'class_label':cls_label,
                    'timestep':t,
                    'lane':self.determine_lane(pose),
                    'initial_state':initial_state}

                new_frame.append(new_obj)

            tf_traj.append(new_frame)

        return tf_traj



##########TEST CASES FOR HOMOGRAPHY CLASS 

def test_homography(hm):
    ''''
    Tests if the fitted matrix matches the training point
    '''
  
    for i in range(4):

        point = hm.config.street_corners[i,:]
        x,y = point
           
        tx, ty = hm.tf_mat.inverse(np.array((x, y)))[0]

       

def test_camera_point(hm,trajectory):
    ''''
    Plots a trajectory on the driving simulator 
    '''
  
    for frame in trajectory:
        for obj in frame:
            x,y,cls_label,t = obj

            x, y = int(hm.config.alberta_img_dim[0] * x), int(hm.config.alberta_img_dim[1]* y)
            hm.vz_debug.visualize_camera_point(x,y,t)
               
            

