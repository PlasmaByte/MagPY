#Created by T. Clayson 28/07/17
#class for handling and studying shock waves

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats



class Shock:
    def __init__(self, shotID=None):
        self.times = [] #lists for holding time and position recordings - typically from multiframe camera
        self.positions = []
        self.shotID = shotID

        #find the shock dynamics file
        if shotID is not None:
            path = "Data/"+shotID
            for subfile in os.listdir(path):
                if "shock dynamics" in subfile.lower():
                    fileName = path+"/"+subfile
            
            #load the file
            with open(fileName) as file:
                for line in file:
                    contents = line.split('\t')
                    if len(contents)>1: #find where we actually have a table
                        if "Time" not in contents[0]:
                            self.times.append( float(contents[0]) )
                            self.positions.append( float(contents[1]) )
                            
            print(self.positions)
            
            
            
    def plot(self, ax=None, color=None):
        if ax is None:
            fig, ax=plt.subplots()

        ax.plot(self.times, self.positions, color=color)
        ax.set_xlabel("Time [ns]")
        ax.set_ylabel("Position [mm]")
        ax.set_title("Shock position over time for "+self.shotID)
        
        #determin shock velocity
        slope, intercept, r_value, p_value, std_err = stats.linregress( self.times,self.positions)
        velocity = slope*1000 #defined in km/s
        velocity_error = std_err*1000
        start_time = -intercept/slope
        ax.plot( [np.amin(self.times),np.amax(self.times)],[ slope*np.amin(self.times)+intercept , slope*np.amax(self.times)+intercept ] , color=color, linestyle ='--' )
        print("Velocity: "+str(velocity)+" +- "+str(velocity_error)+" km/s")
        print("Start time: "+str(start_time)+" ns")
        
        return ax