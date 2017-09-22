#Created by T. Clayson 28/07/17
#class for handling and studying shock waves
#Created by T. Clayson 22/09/17
#class for handling a shock and calculating velocities
#able to measure a liner shock from multiframe cameras

import os
import numpy
import matplotlib.pyplot as plt
from scipy import stats
from SourceCode.Multiframe import Multiframe
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


class Shock:
    def __init__(self, shotID):
        self.shotID = shotID
        self.times = []             #ns
        self.positions = []         #mm
        self.velocity = 0           #km/s
        self.velocity_error = 0     #km/s
        self.start_time = 0         #ns
        self.start_time_error = 0   #ns
        
        self.load_positions()
        
        
        
    def calculate_velocity(self):
        slope, intercept, r_value, p_value, std_err = stats.linregress( self.times,self.positions)
        self.velocity = slope*1000 #defined in km/s
        self.velocity_error = std_err*1000
        self.start_time = -intercept/slope
        
        print("Velocity: "+str(self.velocity)+" +- "+str(self.velocity_error)+" km/s")
        print("Start time: "+str(self.start_time)+" ns")
        
        print("== Linear fit data ==")
        print("Slope: "+str(slope))
        print("Intercept: "+str(intercept))
        print("R value: "+str(r_value))
        print("P value: "+str(p_value))
        print("Standard error: "+str(std_err))



    def load_positions(self):
        if self.shotID is None:
            return
            
        #find the shock dynamics file
        path = "Data/"+self.shotID
        fileName = None
        for subfile in os.listdir(path):
            if "shock dynamics" in subfile.lower():
                fileName = path+"/"+subfile
                
        #if no filename is found we will calculate the shock positions
        if fileName is None:
            print("No shock dynamics file found, measuring positions from multiframe images")
            self.measure_from_multiframe()
            return
        
        #load the file
        with open(fileName) as file:
            for l in file:
                line = l.lower()
                if "velocity" in line:
                    if "error" in line:
                        self.velocity_error = float(line.split('=')[1].strip())
                    else:
                        self.velocity = float(line.split('=')[1].strip())
                if "start" in line:
                    if "error" in line:
                        self.start_time_error = float(line.split('=')[1].strip())
                    else:
                        self.start_time = float(line.split('=')[1].strip())
                    
                contents = line.split('\t')
                if len(contents)>1: #find where we actually have a table
                    if "time" not in contents[0]:
                        self.times.append( float(contents[0]) )
                        self.positions.append( float(contents[1]) )
         
        print("Shock positions loaded: "+fileName)
        return self.positions
            
         
            
    def save_positions(self):
        self.calculate_velocity()
        filename = "Data/"+self.shotID+"/Shock Dynamics"
        with open(filename, 'w') as file:   #writes file
            file.write( "Shock Velocity (km/s) = "+str(self.velocity)+"\n" )
            file.write( "Shock Velocity error (km/s) = "+str(self.velocity_error)+"\n" )
            file.write( "Shock start time (ns) = "+str(self.start_time)+"\n" )
            file.write( "Shock start time error (ns) = "+str(self.start_time_error)+"\n" )
            
            #output all of the shock positions
            file.write( "\nTime (ns)\tPosition(mm)\n" )
            total_points = min( len(self.times), len(self.positions) )
            for i in range(0, total_points ):
                file.write( str(self.times[i])+"\t"+str(self.positions[i])+"\n" )
    
    
    
    def measure_from_multiframe(self, demo=False, ignore_frames=[]):
        import skimage.measure
        
        #make a multiframe camera object
        multiframe = Multiframe(self.shotID)
        self.times = multiframe.frameTimes

        #get lineout from multiframe images averaged over 25 pixels
        lineThickness = 25
        sliceHeight = 500
        lineOuts = []
        for i in range(1,multiframe.frames+1):
            print("Measuring frame "+str(i))
            image = multiframe.getImage(i)
            line = skimage.measure.profile_line( image, (sliceHeight,0),(sliceHeight,1000), linewidth=lineThickness )
            lineOuts.append( line )
        
        #plot lines
        if demo is True:
            fig, ax = plt.subplots()
            for line in lineOuts:
                ax.plot(line)
        
        #plot a few lines for demonstration purposes
        if demo is True:
            fig, axd = plt.subplots()
            axd.plot(lineOuts[3])
            axd.plot(lineOuts[7])
            axd.plot(lineOuts[11])
    
        #determin shock position by finding the first point the line consistently passes the threshold (half the 90th percentile)
        self.positions = []
        for line in lineOuts:
            #threshold ignores first 100 pixels which are not necessarily real
            threshold = np.percentile( line[100:] , 90 )/2
            
            #step through line
            newShockPosition = 0
            pixel = len(line)-100 #ignores irst 100 pixels of noise
            threshold_pixels = 0
            while newShockPosition==0 and pixel>0:
                pixel -= 1
                if line[pixel] > threshold:
                    threshold_pixels += 1
                    if threshold_pixels>20:     #how far to check we are still crossing threshold
                        newShockPosition = (pixel+threshold_pixels)/multiframe.scale + multiframe.offset[0]
            
            self.positions.append(newShockPosition)
    
        #plot this as a graph
        if demo is True:
            self.plot()
            
        
        self.remove_frames(ignore_frames)
        self.save_positions()
            
        
        
    def remove_frames(self, ignore_frames=[]):
        #removes frames we should ignore
        ignore_frames.sort(reverse=True)    #sorts so indecies don't get confused
        for f in ignore_frames:
            del self.times[f]
            del self.positions[f]
            
    
    
    def plot(self, ax=None, color="b", trendline=True):
        if ax is None:
            fig, ax=plt.subplots()
            
        ax.plot(self.times, self.positions, color+'s')   # plots points
        ax.plot(self.times, self.positions, color)  # plot lines
        ax.set_xlabel("Time [ns]")
        ax.set_ylabel("Position [mm]")
        ax.set_title("Shock position over time for "+self.shotID)
        
        #plot linear trendline
        if trendline is True:
            slope = self.velocity/1000
            intercept = -self.start_time*slope
            xValues = numpy.array([ self.times[0], self.times[-1] ])
            yValues = xValues*slope +intercept
            ax.plot( xValues,yValues, color+'--' )
            
        
        return ax