#Created by T. Clayson 04/08/17
#class for analyising and storing data about the MAGPIE pulse generator

import matplotlib.pyplot as plt
from SourceCode.Rogowski import Rogowski
from SourceCode.ScopeChannel import ScopeChannel
from operator import add
import scipy.integrate
import numpy as np



class MAGPIE:
    def __init__(self, shotID=None):
        self.shotID = shotID
        #setup default Rogowski probes
        self.returnPosts = 4
        self.rogowskis = []
        self.rogowskis.append( Rogowski(ScopeChannel(shotID,'2','c1'), 206) )
        self.rogowskis.append( Rogowski(ScopeChannel(shotID,'2','c2'), -216) )
        
        #get average current start from rogowskis
        self.currentStart = 0   #in ns
        for rog in self.rogowskis:
            self.currentStart += rog.currentStart
        self.currentStart /= len(self.rogowskis)
        
        #get dIdt which is a combination of both traces
        self.time = self.rogowskis[0].time
        self.dIdt = np.zeros(len(self.time))
        for rog in self.rogowskis:
            self.dIdt = self.dIdt + rog.data*rog.attenuator*rog.multiplier
        self.dIdt = self.dIdt*self.returnPosts/len(self.rogowskis)    #calculate total dIdt

        #integrate dIdt to get current
        currentStartPos = int(len(self.dIdt)*(self.currentStart-self.time[0])/(self.time[-1]-self.time[0]))
        self.dIdt[:currentStartPos] = 0     #set current before start to zero to ignore initial nosie - is this realistic???
        #self.current = scipy.integrate.cumtrapz( self.dIdt ,self.time )/1e9   #1e9 as time is in ns
        
        self.current = [0]
        for i in range(1,len(self.dIdt)):
            dt = (self.time[i]-self.time[i-1])/1e9
            self.current.append( self.current[i-1] + self.dIdt[i]*dt )

        #self.current = np.append(self.current, self.current[-1] )  #adds extra index to match length of time

        #get max current and peak time
        self.currentMax = max(self.current[:5000])
        self.currentPeak = self.time[np.argmax(self.current[:5000])]
    
        #estimate FWHM from current trace
        self.currentFWHM = 0
        currentFWHMstart = 0
        pos = 200
        while self.currentFWHM==0 and pos<len(self.current)-5:
            pos = pos+1;
            if currentFWHMstart==0:
                #find the first point we consistently pass the threshold
                if self.current[pos]>self.currentMax/2 and self.current[pos+1]>self.currentMax/2:
                    currentFWHMstart = pos
            else:
                #find the point we fall bellow the threshold
                if self.current[pos]<self.currentMax/2 and self.current[pos+1]<self.currentMax/2:
                    self.currentFWHM = (self.time[pos]-self.time[currentFWHMstart])
        
        print("MAGPIE loaded for shot "+shotID)
        print("Current start = "+str(self.currentStart)+" ns with FWHM = "+str(self.currentFWHM)+" ns")
        print("Current maximum = "+str(self.currentMax)+" A at "+str(self.currentPeak)+" ns")
        
        #save to file
        filename = "Data/"+shotID+"/MAGPIE"
        with open(filename, 'w') as file:   #writes file
            file.write( "current start (ns) = "+str(self.currentStart)+"\n" )
            file.write( "current maximum = "+str(self.currentMax)+"\n" )
            file.write( "current FWHM (ns) = "+str(self.currentFWHM)+"\n" )
            file.write( "current peak (ns) = "+str(self.currentPeak)+"\n" )
        
        
        
    def plotRogowskis(self, ax=None):
        if ax is None:
            fig, ax=plt.subplots()
        for rog in self.rogowskis:
            ax.plot(rog.time[:-10], rog.data[:-10])
        plt.xlabel("Time [ns]")
        plt.ylabel("Voltage [V]")
        plt.title("Readings from Rogowskis for shot "+self.shotID)
        plt.xlim( [0,3000] )
        return ax
        
        
            
    def plotCurrent(self, ax=None):
        if ax is None:
            fig, ax=plt.subplots()
        ax.plot(self.time, self.current, linestyle='--')
        plt.xlabel("Time [ns]")
        plt.ylabel("Current [A]")
        plt.title("MAGPIE current for shot "+self.shotID)
        plt.xlim( [0,3000] )
        return ax
        
        
        
    def plot(self, plotType='current', ax=None, label=None, color=None, linestyle=None):
        if ax is None:  #create plot if none exists
            fig, ax=plt.subplots()
            
        #select the data type to plot
        data1,label1 = None,""
        data2,label2 = None,""
        if "current" in plotType.lower():
            data1,label1 = self.current,"current "+self.shotID
        if "didt" in plotType.lower():
            if "total" in plotType.lower():
                data1,label1 = self.dIdt,"Total dIdt "+self.shotID
            else:
                data1,label1 = self.rogowskis[0].data*self.rogowskis[0].attenuator*self.rogowskis[0].multiplier ,"Probe 1 dIdt "+self.shotID
                data2,label2 = self.rogowskis[1].data*self.rogowskis[1].attenuator*self.rogowskis[1].multiplier ,"Probe 2 dIdt "+self.shotID
        if "raw" in plotType.lower() or "voltage" in plotType.lower():
            data1,label1 = self.rogowskis[0].data,"Probe 1 "+self.shotID
            data2,label2 = self.rogowskis[1].data,"probe 2 "+self.shotID
            
        if label is not None:   #set labels if we pass them to the function
            label1 = label
            
        if data1 is not None:
            ax.plot(self.time, data1, label=label1,color=color,linestyle=linestyle)
        if data2 is not None:
            ax.plot(self.time, data2, label=label2)

        #set axis
        ax.set_xlabel("Time [ns]")
        ax.set_xlim( [1000,2500] )
        ax.legend()
        if "current" in plotType.lower():
            ax.set_title("MAGPIE current for "+self.shotID)
            ax.set_ylabel("Current [A]")
        if "didt" in plotType.lower():
            ax.set_title("Total dI/dt for "+self.shotID)
            ax.set_ylabel("dI/dt [A/s]")
        if "raw" in plotType.lower() or "voltage" in plotType.lower():
            ax.set_title("Raw signal voltages for Rogowski probes for "+self.shotID)
            ax.set_ylabel("Voltage [V]")
        
        return ax