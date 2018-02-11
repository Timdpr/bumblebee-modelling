"""
A model of a hive and a number of flowers, with a focus on analysing the role
of public vs private information in bee foraging. Currently unfinished!
Inspired by 'The honeybee waggle dance[...]' (Grüter & Farina, 2009)

@author: tp275
"""
import numpy as np
import random
import matplotlib.pyplot as plt

class Bee:
    def __init__(self, bee_id, ):
        self.bee_id = bee_id
        self.state = 0 # 0=idle in nest, 1=performing waggle dance, 2=foraging
        self.foragingTurns = 0
        self.waggle_turns = 0 # how many turns left in waggle dance state
        self.waggle_direction = 0
        self.public_direction = 0
        self.private_direction = [] # list of the bee's own stored directions

    def speak(self):
        print(str(self.bee_id) + " says: BUZZ!")


class BeeStats:
    def __init__(self, timesteps):
        self.timesteps = timesteps
        self.num_idle = []
        self.num_waggle = []
        self.num_forage = []
        self.site_numbers = []
        self.site_matrix = np.zeros((timesteps, 8))
        
    def add_to_state_stats(self, bees):
        """
        Given list of bees, totals up how many are in each state and appends
        that total to lists of state totals. To be called per timestep.
        """
        idle = 0
        waggle = 0
        forage = 0
        for b in bees:
            if b.state == 0:
                idle += 1
            elif b.state == 1:
                waggle += 1
            elif b.state == 2:
                forage += 1
        self.num_idle.append(idle)
        self.num_waggle.append(waggle)
        self.num_forage.append(forage)
                
    def show_state_stats(self):
        plt.plot(range(timesteps+1), self.num_idle, label="Bees idle in nest")
        plt.plot(range(timesteps+1), self.num_waggle, label="Bees performing waggle dance")
        plt.plot(range(timesteps+1), self.num_forage, label="Bees foraging")
        plt.legend()
        
    def add_to_site_stats(self, site_numbers):
        """Appends, per timestep, a dictionary containing sites:#bees in that site
        """
        self.site_numbers.append(site_numbers)
        
    def show_site_stats(self):
        """
        Creates a matrix containing numbers of bees in the different sites at each timestep:
        8 columns represent sites, rows are per timestep, values are the number of bees in the site
        This is then used to plot the number of bees at all sites per timestep,
        as well as other purposes in other methods
        """
        for i in range(self.timesteps):
            self.site_matrix[i] = list(self.site_numbers[i].values())
        
        plt.plot(range(self.timesteps), [np.sum(self.site_matrix[i]) for i in range(self.timesteps)], label="Bees at sites")
        plt.legend()
        plt.show()
        
    def show_total_quality(self):
        """
        Plots, using the site_matrix and a dictionary of sites and their qualities,
        the total site quality experienced by all currently foraging bees
        (total = sum(each foraging bee * its site quality))
        Also plotted is the mean calculated using 'bin' sizes set by numForMean
        """
        sites = {0:100, 1:10, 2:50, 3:10, 4:100, 5:10, 6:50, 7:10}
        timesteps = len(self.site_numbers)
        qualities = []
        for i in range(timesteps):
            total = 0
            row = self.site_matrix[i]
            for j in range(8):
                total += (row[j] * sites.get(j))
            qualities.append(total)
        plt.plot(range(timesteps), qualities, label="Total quality")
        
        numForMean = 50
        avQualities = []
        for i in range(int(timesteps/numForMean)):
            avQualities.append(np.mean(qualities[i*numForMean:(i+1)*numForMean]))
        plt.plot(range(0, timesteps, numForMean), avQualities, 'r', linewidth=3, label="Average quality")

        plt.legend()
        

def recruit(bees, waggle_direction):
    """
    Goes through idle bees, turns them into foraging bees with certain probability
    Foraging bees have a 'public' direction assigned from the waggle dancing bee, +- some error
    """
    for b in bees:
        if b.state == 0:
            if random.random() < 0.1:
                b.state = 2 # recruit bee to foraging
                b.foragingTurns = 2
                b.public_direction = waggle_direction + random.randrange(-90,90)
                
def work_out_direction(bee, use_public): # TODO:
    """
    Determines and returns a location for a foraging bee to go to
    """
    if use_public:
        return bee.public_direction
        # TODO: some mix of private and public info. Perhaps use public to set a good private location
    else:
        # TODO: return one of the bee's private directions if it has any.
        if not bee.private_direction:
            return random.randrange(0,360)
        return random.choice(bee.private_direction)
    
def use_public_location():
    """
    Returns boolean which is checked to determine whether a bee should consider
    public information in its direction calculation
    """
    #return random.choice([True, False])
    if random.random() < 0.1:
        return False
    return True


if __name__ == "__main__":
    
    bees = [Bee(i) for i in range(500)] # create list of bees
    
    # Set up some bees to be initially waggling:
    bees[0].state = 1
    bees[0].waggle_turns = 5
    bees[0].waggle_direction = 90
    
    bees[1].state = 1
    bees[1].waggle_turns = 1
    bees[1].waggle_direction = 225
    
    bees[2].state = 1
    bees[2].waggle_turns = 5
    bees[2].waggle_direction = 90
    
    bees[3].state = 1
    bees[3].waggle_turns = 1
    bees[3].waggle_direction = 225
    
    #####
    timesteps = 1000 # how many turns to go through every bee and perform action    
    #####
    
    sites = {0:100, 45:10, 90:50, 135:10, 180:100, 225:10, 270:50, 315:10} # location :quality
    stats = BeeStats(timesteps)
    stats.add_to_state_stats(bees)
        
    for i in range(timesteps):
        
        if i % 20 == 0:
            print("\nTimestep: " + str(i))
            
        site_numbers = {0:0, 45:0, 90:0, 135:0, 180:0, 225:0, 270:0, 315:0}
        for bee in bees:
            #print(bee.state)
            
            # if bee is idle in nest, do nothing # TODO: With some small chance, leave without seeing waggle dance
            if bee.state == 0:
                continue
            
            # if bee is waggle dancing
            elif bee.state == 1:
                recruit(bees, bee.waggle_direction) # recruit idle bees
                bee.waggle_turns -= 1
                if bee.waggle_turns <= 0:
                    bee.state = 0
                    
            # if bee is foraging
            elif bee.state == 2:
                if bee.foragingTurns < 0:
                    use_public = use_public_location()
                    direction = work_out_direction(bee, use_public)
                    if direction in sites:
                        # TODO: DO STATS
                        site_numbers[direction] += 1
                        bee.state = 1
                        bee.waggle_turns = sites.get(direction)/10
                        bee.waggle_direction = direction
                        bee.private_direction.append(direction)
                    else:
                        # TODO: stats
                        bee.state = 0
                else:
                    bee.foragingTurns -= 1
                    
        stats.add_to_state_stats(bees)
        stats.add_to_site_stats(site_numbers)
    stats.show_state_stats()
    stats.show_site_stats()
    stats.show_total_quality()