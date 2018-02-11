# -*- coding: utf-8 -*-
"""
Intelligence in Animals and Machines, Assessment 3
Module containing the bee class, used in the main simulation

@author: tp275
"""
import numpy as np
import sys
from sklearn.preprocessing import normalize

class Bee:
    """
    A single bee, used in one run of the model.
    A neat way of storing useful variables and methods for use by the main loop.
    """
    def __init__(self, set_2013_probs):
        """
        Matrix representing distances between sites.
        0     1        2   3   4   5
        nest, flower1, f2, f3, f4, f5
        """
        self.distance_matrix = [[0,   50,  100, 120, 100, 50],
                                [50,  0,   50,  80,  80,  50],
                                [100, 50,  0,   50,  80,  80],
                                [120, 80,  50,  0,   50,  80],
                                [100, 80,  80,  50,  0,   50],
                                [50,  50,  80,  80,  50,  0 ]]
        # enable this to manipulate the scale, as discussed in the 2013 paper:
#        self.distance_matrix = np.divide(self.distance_matrix, 10)

        """
        Matrix representing the probability of the bee transitioning between flower pairs.
        Probabilities set as per Lihoreau 2012, with 0.1 for near and 0.6 for far.
        Same indexes as distance_matrix.
        """
        self.transition_probability_matrix = [[0,   0.8, 0.0, 0.0, 0.0, 0.2],
                                              [0.6, 0,   0.6, 0.1, 0.1, 0.6],
                                              [0.1, 0.6, 0,   0.6, 0.1, 0.1],
                                              [0.1, 0.1, 0.6, 0,   0.6, 0.1],
                                              [0.1, 0.1, 0.1, 0.6, 0,   0.6],
                                              [0.6, 0.6, 0.1, 0.1, 0.6, 0  ]]
        self.normalize_probability_matrix()
        
        if set_2013_probs:
            self.set_distance_style_probabilities()

        # A 6*6 matrix to record each transition between locations
        self.transition_recording_matrix = []
        self.reset_transition_matrix()

        # the bee's current location
        self.location = 0

        # set of unique visited locations
        self.unique_visited_locations = set([])
        
        # list of all visited locations in order
        self.visited_locations = []
        
        # the current minimum total bout distance found in this run
        self.min_distance = sys.maxsize
        
    def move(self):
        """Undertakes one location-to-location move of the bee
        """
        # calculate the bee's next location
        dest = self.get_destination()
        
        # record the transition
        self.transition_recording_matrix[self.location][dest] += 1
        
        # update the bee's location
        self.location = dest
        
        # add the new location to location lists
        self.unique_visited_locations.add(self.location)
        self.visited_locations.append(self.location)
      
    def get_destination(self):
        """Returns the next location for the bee, calculated using the probability matrix
        """
        return np.random.choice([0,1,2,3,4,5], p=self.transition_probability_matrix[self.location])
        # when enabled, the following disallows choosing the previous location:
#        if len(self.visited_locations) > 1:
#            while choice == self.visited_locations[-2]:
#                choice = np.random.choice([0,1,2,3,4,5], p=self.transition_probability_matrix[self.location])
#        return choice
        
    def get_total_distance(self):
        """Returns the summed distance of all transitions currently stored
        """
        return np.sum(np.multiply(self.distance_matrix, self.transition_recording_matrix))
    
    def reset_transition_matrix(self):
        """Sets the transiton recording matrix to all zeros
        """
        self.transition_recording_matrix = np.zeros((6,6), dtype=int)
    
    def normalize_probability_matrix(self):
        """Goes through each row of the probability matrix and normalizes the values (0-1)
        """
        self.transition_probability_matrix = normalize(self.transition_probability_matrix,
                                                       axis=1, norm='l1')
                                                       
    def update_probability_matrix(self, prob_enhancement_factor):
        """
        Updates the probability matrix, heightening probabilities of the transitions
        in the bout currently stored in the transition_recording_matrix by a given factor
        """
        # create a matrix to multiply the probability matrix with
        mult_mat = np.multiply(self.transition_recording_matrix, prob_enhancement_factor)
        # make all 0s 1s, so probs remain the same when multiplied by this matrix
        np.place(mult_mat, mult_mat == 0, 1)
        self.transition_probability_matrix = np.multiply(self.transition_probability_matrix, mult_mat)
        self.normalize_probability_matrix() # don't forget to normalize those probabilities!

    def set_distance_style_probabilities(self):
        """
        Sets the initial transition probability matrix as per the 2013 paper.
        Probabilities are inversely proportional to the squared distance between flowers,
        normalized with respect to all flowers.
        """
        new_probs = np.copy(self.distance_matrix)
        new_probs = np.power(new_probs, 2)
        for i, row in enumerate(new_probs):
            row_sum = sum(row)
            for j in range(len(new_probs)):
                if row[j] != 0:
                    row[j] = row_sum - row[j]
        self.transition_probability_matrix = new_probs
        self.normalize_probability_matrix()
        