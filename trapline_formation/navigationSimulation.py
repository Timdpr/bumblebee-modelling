# -*- coding: utf-8 -*-
"""
Intelligence in Animals and Machines, Assessment 3
The main simulation, using the Bee class

A from-scratch replication of the model loosely described in 'Radar Tracking
and Motion-Sensitive Cameras on Flowers Reveal the Development of Pollinator
Multi-Destination Routes over Large Spatial Scales’ (Lihoreau et al., 2012)

@author: tp275
"""
import singleBee
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

########## PARAMETERS ##########
        
bouts = 250 # the number of foraging 'bouts': runs for the bee to complete
runs = 1000 # the number of times to run the bouts, essentially number of bees
prob_enhancement_factor = 2.5 # the probability enhancement factor

set_2013_probs = False # toggles whether initial probabilities use distance

novelty_extension = False # toggles smaller enhancement factor for duplicate bouts
swap_point = 50 # roughly how many duplicates it takes to start decreasing probability

plot_run_graphs = False # [bout, distance] graph of each run
print_average_distances = True
plot_average_distance_graph = False
plot_histograms = True
bins = int(bouts/10*2)


########## MAIN LOOP ##########

if __name__ == "__main__":
    av_distances = [[] for i in range(5)] # holds the average distances of slices of each run
    locations_all_runs = [[] for i in range(runs)] # holds list of locations in each bout for each run
    
    for r in range(runs):
        if (r+1) % 100 == 0:
            print("\n**********\nRun " + str(r+1) + "\n**********")
        bee = singleBee.Bee(set_2013_probs) # create bee
        distances = [] # holds total distance covered in each bout
   
        b = 0
        while b < bouts:
            complete_run = True # set false when bee returns w/o visiting all flowers

            # reset all location records with bee in nest, also transition record
            bee.location = 0
            bee.unique_visited_locations = set([0])
            bee.visited_locations = [0]
            bee.reset_transition_matrix()
            
            # bee movement loops while it hasn't visited all locations
            while len(bee.unique_visited_locations) < 6:
                bee.move()
                # if bee returns to nest before this, end and mark bout as incomplete
                if bee.location == 0:
                    complete_run = False
                    break
                
            # if bee visited all locations, return to nest:
            if complete_run: 
                bee.transition_recording_matrix[bee.location][0] += 1
                bee.visited_locations.append(0)
            
            # could set bouts to increment only if run is complete (indent all below)
            b += 1
            locations_all_runs[r].append(bee.visited_locations)
            
            # append summed distance of bout to list
            distances.append(bee.get_total_distance())
            
            # if distance is new shortest route
            if bee.get_total_distance() <= bee.min_distance and complete_run:
                # set new min distance
                bee.min_distance = bee.get_total_distance()
                # then update transition probabilities....
               
                ####### My extension #######
                if novelty_extension:
                    # prob. enhancement factor diminishes and goes negative pE = pE-(2*(copies/50))
                    repeats = locations_all_runs[r].count(bee.visited_locations)
                    bee.update_probability_matrix(prob_enhancement_factor-(1.1*(repeats/swap_point)))
                else:
                    bee.update_probability_matrix(prob_enhancement_factor)


########## PLOTTING ##########
                
        ## plot all bout distances for this run: ##       
        if plot_run_graphs:
            plt.xlabel("Bouts")
            plt.ylabel("Total bout distance")
            plt.ylim(0,900)
            plt.plot(range(bouts), distances)
            # plot average of every 'x' bout distances on same graph:
            # split distances into 'bins':
            dist_split = np.array_split(distances.copy(), (int(bouts/10)+1))
            dist_avs = [] # create list of averages of those bins:
            for dists in dist_split:
                dist_avs.append(np.mean(dists))
            plt.plot(range(0, bouts+1, int(bouts/(bouts/10))), dist_avs, color='r', linewidth=2)
            plt.show()
            plt.clf()
        
    ## plot the run and run slice distance averages ##
        if print_average_distances:  
            b_h = int(bouts/2) # int, == half the amount of bouts
            b_q = int(bouts/4) # int, == quarter the amount of bouts
            # append mean distance of this run,
            # and of certain chunks/slices of this run, to a list of lists
            av_distances[0].append(np.mean(distances))
            av_distances[1].append(np.mean(distances[:b_q])) # 1st quarter
#            av_distances[2].append(np.mean(distances[b_q:b_h]))
#            av_distances[3].append(np.mean(distances[b_h:(b_q)*3]))
            av_distances[4].append(np.mean(distances[(b_q)*3:])) # 4th quarter
            
    print("Mean distance in all runs: " + str(np.mean(av_distances[0])))
    print("Mean 1st quarter distance in all runs: " + str(np.mean(av_distances[1])))
    print("Mean 4th quarter distance in all runs: " + str(np.mean(av_distances[4])))
    print()
    print("Median distance in all runs: " + str(np.median(av_distances[0])))
    print("Median 1st quarter distance in all runs: " + str(np.median(av_distances[1])))
    print("Median 4th quarter distance in all runs: " + str(np.median(av_distances[4])))
    print()
    
    if plot_average_distance_graph: 
        plt.ylim(200,1250)
        plt.xlim(1,runs)
        plt.plot(range(1,runs+1), av_distances[0], color='r', marker='o', label="Average distances")
        plt.plot(range(1,runs+1), av_distances[1], color='g', marker='o', label="Av. dist. 1st q")
        plt.plot(range(1,runs+1), av_distances[4], color='b', marker='o', label="Av. dist. 4th q")
        plt.legend()
        plt.show()
        plt.clf()
    
    ## interpret optimum and unique run data ##
    bouts_to_optimum = []
    bouts_to_stable_optimum = []
    unique_list = []
    for r, run in enumerate(locations_all_runs):
        # bouts to first optimum
        if [0,1,2,3,4,5,0] in run:
            bouts_to_optimum.append(run.index([0,1,2,3,4,5,0])+1)
        elif [0,5,4,3,2,1,0] in run:
            bouts_to_optimum.append(run.index([0,5,4,3,2,1,0])+1)
#        else:
#            bouts_to_optimum.append(math.nan)
        
        # number of unique bouts in a run
        unique_list.append(len(set(tuple(bout) for bout in run)))
        
        # bouts to stable optimum
        stable = False
        for b in range(2, len(locations_all_runs[r])):
            if run[b] == run[b-1] and run[b] == run[b-2]:
                if run[b] == [0,1,2,3,4,5,0] or run[b] == [0,5,4,3,2,1,0]:
                    bouts_to_stable_optimum.append(b-1)
                    stable = True
                    break
#        if not stable:
#            bouts_to_stable_optimum.append(math.nan)
    
    ## plot histograms of optimum and unique run data ##
    if plot_histograms:
        print("Number of runs that reached the optimum: "
              + str(len(bouts_to_optimum)) + "/" + str(runs))
        
        print("\nMean bouts to first optimum: " + str(np.mean(bouts_to_optimum)))
        print("Empirical mean: " + str(18))
        print(stats.ttest_1samp(bouts_to_optimum, 18.0)[1])
        
        print("\nMean bouts to stable optimum: " + str(np.mean(bouts_to_stable_optimum)))
        print("Empirical mean: " + str(27))
        print(stats.ttest_1samp(bouts_to_stable_optimum, 27.0)[1])
        
        print("\nMean number of unique bouts: " + str(np.mean(unique_list)))
        
        plt.title("Bouts to first optimum")
        plt.xlabel("Number of bouts")
        plt.ylabel("Runs")
        plt.xlim(0,bouts)
        plt.hist(bouts_to_optimum, bins=bins)
        plt.show()
        plt.clf()
        
        plt.title("Bouts to stable optimum")
        plt.xlabel("Number of bouts")
        plt.ylabel("Runs")
        plt.xlim(0,bouts)
        plt.hist(bouts_to_stable_optimum, bins=bins)
        plt.show()
        plt.clf()
        
        plt.title("Number of unique bouts in a run")
        plt.xlabel("Number of unique bouts")
        plt.ylabel("Runs")
        plt.xlim(0,bouts)
        plt.hist(unique_list, bins=bins)
        plt.show()
        plt.clf()
