#Created by T. Clayson 14/09/17

import os
from SourceCode.Multiframe import Multiframe
from SourceCode.ShotData import ShotData
from SourceCode.BdotPair import BdotPair
from SourceCode.Interferometry import Interferometry
from SourceCode.MAGPIE import MAGPIE
from SourceCode.Gases import Gases
import skimage.measure
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats



class ShockVelocity:
    def __init__(self, shotData):
        self.shotData = shotData
        return
     
    
    
    def saveVelocity(self):
        filename = "Data/"+self.shotData.shotID+"/Shock Dynamics"
        with open(filename, 'w') as file:   #writes file
            file.write( "Shock Velocity (km/s) = "+str(velocity)+"\n" )
            file.write( "Shock Velocity error (km/s) = "+str(velocity_error)+"\n" )
            file.write( "Shock start time (ns) = "+str(start_time)+"\n" )
            
            #output all of the shock positions
            file.write( "\nTime (ns)\tPosition(mm)\n" )
            for i in range(0,self.multiframe.frames):
                file.write( str(self.multiframe.frameTimes[i])+"\t"+str(shockPositions[i])+"\n" )
        
        return
    
    
    
    def loadVelocity(self):
        return
    
    
    
    def measureVelocity(self):
        # measure the velocity from 12 frame images
        if not hasattr(self,"multiframe"):  #check we imported multiframe camera
            return

        #get lineout from multiframe images averaged over 25 pixels
        lineThickness = 25
        sliceHeight = 500
        lineOuts = []
        for i in range(1,self.multiframe.frames+1):
            print("Measuring frame "+str(i))
            image = self.multiframe.getImage(i)
            line = skimage.measure.profile_line( image, (sliceHeight,0),(sliceHeight,1000), linewidth=lineThickness )
            lineOuts.append( line )
            
        #plot lines
        fig, ax = plt.subplots()
        for line in lineOuts:
            ax.plot(line)
            
         #plot a few lines for demonstration purposes
        fig, axd = plt.subplots()
        axd.plot(lineOuts[3])
        axd.plot(lineOuts[7])
        axd.plot(lineOuts[11])
        
        #determin shock position by finding the first point the line consistently passes the threshold (half the 90th percentile)
        shockPositions = []
        for line in lineOuts:
            #threshold ignores first 100 pixels which are not necessarily real
            threshold = max(line[100:])/2 #np.percentile( line[100:] , 90 )/2
            
            #step through line
            newShockPosition = 0
            pixel = len(line)-100 #ignores first 100 pixels of noise
            while newShockPosition==0 and pixel>0:
                pixel -= 1
                if line[pixel] > threshold:
                    newShockPosition = pixel/self.multiframe.scale + self.multiframe.offset[0]
            
            shockPositions.append(newShockPosition)

        #determin shock velocity
        slope, intercept, r_value, p_value, std_err = stats.linregress( self.multiframe.frameTimes ,shockPositions)
        velocity = slope*1000 #defined in km/s
        velocity_error = std_err*1000
        start_time = -intercept/slope
        ax2.plot( [np.amin(self.multiframe.frameTimes),np.amax(self.multiframe.frameTimes)],[ slope*np.amin(self.multiframe.frameTimes)+intercept , slope*np.amax(self.multiframe.frameTimes)+intercept ] )
        print("Velocity: "+str(velocity)+" +- "+str(velocity_error)+" km/s")
        print("Start time: "+str(start_time)+" ns")

        return velocity
    
    
    
    def plot(self, ax=None):
        if ax is None:
            fig, ax = plt.subplots()
            
        ax.plot(self.multiframe.frameTimes, shockPositions, 'bs')   # plots points
        ax.plot(self.multiframe.frameTimes, shockPositions, 'b--')  # plot lines
        plt.xlabel('Time [ns]')
        plt.ylabel('Position [mm]')
        return ax