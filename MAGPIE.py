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
        self.currentStart_error = 0
        error_per_value = 0
        for rog in self.rogowskis:
            self.currentStart += rog.currentStart
            self.currentStart_error += rog.currentStart_error
            error_per_value += np.square( rog.noise_range*rog.attenuator*rog.multiplier ) #errors add in quadrature
        error_per_value = np.sqrt(error_per_value)
        self.currentStart /= len(self.rogowskis)
        self.currentStart_error /= len(self.rogowskis)
        
        #get dIdt which is a combination of both traces
        self.time = self.rogowskis[0].time
        self.dIdt = np.zeros(len(self.time))
        for rog in self.rogowskis:
            self.dIdt = self.dIdt + rog.data*rog.attenuator*rog.multiplier
        self.dIdt = self.dIdt*self.returnPosts/len(self.rogowskis)    #calculate total dIdt

        #integrate dIdt to get current
        currentStartPos = int(len(self.dIdt)*(self.currentStart-self.time[0])/(self.time[-1]-self.time[0]))
        self.dIdt[:currentStartPos] = 0     #set current before start to zero to ignore initial nosie - is this realistic???        
        
        self.current = [0]
        self.current_error = [0]
        for i in range(1,len(self.dIdt)):   #yeah! manual integration!!!
            dt = (self.time[i]-self.time[i-1])/1e9
            self.current.append( self.current[i-1] + self.dIdt[i]*dt )
            if self.time[i]<self.currentStart:
                self.current_error.append(0)
            else:
                self.current_error.append( self.current_error[i-1] + error_per_value*dt)        

        #calculate error arrays = min and max currents at all times - for calculating errors
        errorsMin = np.array(self.current) - np.array(self.current_error)
        errorsMax = np.array(self.current) + np.array(self.current_error)

        #get max current and peak time
        self.currentMax = max(self.current[:5000])
        currentMax_position = np.argmax(self.current[:5000])
        self.currentMax_error = ( max(errorsMax[:5000]) - max(errorsMin[:5000]) )/2
        self.currentPeak = self.time[currentMax_position]
        
        #error on peak time is width of top section
        # = time errror max > max (errorMin)
        min_current_peak = max(errorsMin)
        current_peak_start = 0
        self.current_peak_error = 0
        for i in range(1,len(self.current)):
            if errorsMax[i]>min_current_peak and current_peak_start==0:
                current_peak_start = self.time[i]
            if errorsMax[i]<min_current_peak and current_peak_start>0:
                self.current_peak_error = (self.time[i]-current_peak_start)/2
                break
        
        #estimate FWFM from current trace
        #get FWFM error from width of FWFM of errormax
        self.currentFWFM = 0
        self.currentFWFM_error = 0
        currentFWFMstart = 0
        currentFWFMstart_error = 0
        FWFM_error_current = self.currentMax-self.currentMax_error
        pos = 200
        while (self.currentFWFM==0 or self.currentFWFM_error==0) and pos<len(self.current)-5:
            pos = pos+1;
            if currentFWFMstart==0:
                #find the first point we consistently pass the threshold
                if self.current[pos]>self.currentMax/2 and self.current[pos+1]>self.currentMax/2:
                    currentFWFMstart = pos
            else:
                #find the point we fall bellow the threshold
                if self.current[pos]<self.currentMax/2 and self.current[pos+1]<self.currentMax/2:
                    self.currentFWFM = (self.time[pos]-self.time[currentFWFMstart])
                    
            if currentFWFMstart_error==0:
                #find the first point we consistently pass the threshold
                if errorsMax[pos]>FWFM_error_current/2 and errorsMax[pos+1]>FWFM_error_current/2:
                    currentFWFMstart_error = pos
            else:
                #find the point we fall bellow the threshold
                if errorsMax[pos]<FWFM_error_current/2 and errorsMax[pos+1]<FWFM_error_current/2:
                    #store maximum FWFM here for a moment
                    self.currentFWFM_error = (self.time[pos]-self.time[currentFWFMstart_error])
                    
        self.currentFWFM_error = self.currentFWFM_error-self.currentFWFM
        
        print("MAGPIE loaded for shot "+shotID)
        print("Current start = "+str(self.currentStart)+" +- "+str(self.currentStart_error)+" ns")
        print("FWHM = "+str(self.currentFWFM)+" +- "+str(self.currentFWFM_error)+" ns")
        print("Current maximum = "+str(self.currentMax)+" +- "+str(self.currentMax_error)+" A")
        print("Current peak at "+str(self.currentPeak)+" +- "+str(self.current_peak_error)+" ns")
        
        #save to file
        filename = "Data/"+shotID+"/MAGPIE"
        with open(filename, 'w') as file:   #writes file
            file.write( "current start (ns) = "+str(self.currentStart)+"\n" )
            file.write( "current maximum (A) = "+str(self.currentMax)+"\n" )
            file.write( "current FWFM (ns) = "+str(self.currentFWFM)+"\n" )
            file.write( "current peak time (ns) = "+str(self.currentPeak)+"\n" )
            file.write( "\n" )
            file.write( "current start error (ns) = "+str(self.currentStart_error)+"\n" )
            file.write( "current maximus error (A) = "+str(self.currentMax_error)+"\n" )
            file.write( "current FWFM error (ns) = "+str(self.currentFWFM_error)+"\n" )
            file.write( "current peak time error (ns) = "+str(self.current_peak_error)+"\n" )

        
        
    def plot(self, plotType='current', ax=None, label=None, color=None, linestyle=None, times = [0,1500]):
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
            if "1" in plotType:
                data1,label1 = self.rogowskis[0].data,"Probe 1 "+self.shotID
            elif "2" in plotType:
                data1,label1 = self.rogowskis[1].data,"Probe 2 "+self.shotID
            else:
                data1,label1 = self.rogowskis[0].data,"Probe 1 "+self.shotID
                data2,label2 = self.rogowskis[1].data,"probe 2 "+self.shotID
            
        if label is not None:   #set labels if we pass them to the function
            label1 = label

        #apply current offset
        plot_times = np.array(self.time) - self.currentStart
            
        #plot errors in current case
        if "current" in plotType.lower():
            errorsMin = np.array(self.current) - np.array(self.current_error)
            errorsMax = np.array(self.current) + np.array(self.current_error)
            ax.fill_between(plot_times, errorsMin,errorsMax, facecolor=color, alpha=.5)

        #plot data            
        if data1 is not None:
            ax.plot(plot_times, data1, label=label1,color=color,linestyle=linestyle)
        if data2 is not None:
            ax.plot(plot_times, data2, label=label2)

        #set axis
        ax.set_xlabel("Time [ns]")
        ax.set_xlim( times )
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