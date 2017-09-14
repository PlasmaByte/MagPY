#Created by T. Clayson 28/07/17

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



class LinerExperiment:
    def __init__(self, shotID):
        #find the shotdata folder on Linna
        self.shotData = ShotData(shotID)
        
        #variables with defaults
        self.dataPath = "Data/"+shotID+"/"
        self.linerMaterial = "stainless steel"
        self.linerThickness = 100;
        self.gasFill = "Argon"
        self.gasPressure = 24
        
        #diagnostics
        self.multiframe = None
        self.bdotPairs = []
        self.interferometry = []
        
        #load up MAGPIE class
        self.MAGPIE = MAGPIE(shotID)

        #find liner experiment file and load its data
        filename = self.dataPath+"Liner Experiment"
        if not os.path.isfile(filename):    #check we have the file
            print("No file found: "+filename)
            return
            
        #open shot file and read line by line to load all data
        with open(filename) as file:
            for l in file:
                line = l.lower()

                if "liner material" in line:
                    self.linerMaterial = line.split('=')[1].strip()
                
                if "liner thickness" in line:
                    self.linerThickness = float(line.split('=')[1].strip())
                    
                if "gas fill" in line:
                    self.gasFill = line.split('=')[1].strip()
                    
                if "gas pressure" in line:
                    self.gasPressure = float(line.split('=')[1].strip())
                    
                if "<multiframe>" in line:    #setup multiframe
                    print("load Multiframe")
                    self.multiframe = Multiframe(file=file, shotData=self.shotData)
                    
                if "<interferometry>" in line:    #setup interferometry
                    print("load Interferometry")
                    self.interferometry.append( Interferometry(file=file, shotData=self.shotData) )
                
                if "<bdot pair>" in line:    #setup Bdot pair
                    print("load Bdot")
                    self.bdotPairs.append( BdotPair(file=file, shotID=shotID) )
                      
    
                    
    def getInterferometry(self, wavelength=10):  #easy method for finding interferometry of specific wavelengths
        for inter in self.interferometry:
            if inter.wavelength==wavelength:
                return inter
        
                
                
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
            
        #plot this as a graph
        fig, ax2 = plt.subplots()
        ax2.plot(self.multiframe.frameTimes, shockPositions)
        plt.xlabel('Time [ns]')
        plt.ylabel('Position [mm]')
        
        #determin shock velocity
        slope, intercept, r_value, p_value, std_err = stats.linregress( self.multiframe.frameTimes ,shockPositions)
        velocity = slope*1000 #defined in km/s
        velocity_error = std_err*1000
        start_time = -intercept/slope
        ax2.plot( [np.amin(self.multiframe.frameTimes),np.amax(self.multiframe.frameTimes)],[ slope*np.amin(self.multiframe.frameTimes)+intercept , slope*np.amax(self.multiframe.frameTimes)+intercept ] )
        print("Velocity: "+str(velocity)+" +- "+str(velocity_error)+" km/s")
        print("Start time: "+str(start_time)+" ns")
        
        #save calculated velocity to file
        filename = "Data/"+self.shotData.shotID+"/Shock Dynamics"
        with open(filename, 'w') as file:   #writes file
            file.write( "Shock Velocity (km/s) = "+str(velocity)+"\n" )
            file.write( "Shock Velocity error (km/s) = "+str(velocity_error)+"\n" )
            file.write( "Shock start time (ns) = "+str(start_time)+"\n" )
            
            #output all of the shock positions
            file.write( "\nTime (ns)\tPosition(mm)\n" )
            for i in range(0,self.multiframe.frames):
                file.write( str(self.multiframe.frameTimes[i])+"\t"+str(shockPositions[i])+"\n" )
            
        return velocity