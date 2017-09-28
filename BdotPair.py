#Created by T. Clayson 07/08/17
#object for handling a Bdot pair probe

import numpy as np
import scipy.integrate
from SourceCode.ScopeChannel import ScopeChannel
from SourceCode.BdotProbe import BdotProbe
from SourceCode.MAGPIE import MAGPIE
import matplotlib.pyplot as plt



class BdotPair:
    def __init__(self, shotID=None, file=None, Bdot1=None, Bdot2=None):
        
        self.shotID = shotID
        self.Bdot1 = None   #a Bdot pair is made of 2 seperate BdotProbe objects
        self.Bdot2 = None
        
        #save Bdots if we have them
        if (Bdot1 is not None) and (Bdot2 is not None):
            self.Bdot1 = Bdot1
            self.Bdot2 = Bdot2
        
        #load Bdot file and create probes if instructed to do so
        if file is not None:
            self.readFile(file)
    
        if (self.Bdot1 is None) or (self.Bdot1 is None): #escape if we are missing Bdots
            print("Missing Bdot :(")
            return;
            
        self.time = self.Bdot1.time
        
        #calculate the E field
        self.Efield = (self.Bdot1.data * self.Bdot1.attenuator + self.Bdot2.data * self.Bdot2.attenuator)/2
        
        #calculatethe dB/dt and B field
        self.dBdt = (self.Bdot1.data * self.Bdot1.attenuator / self.Bdot1.area - self.Bdot2.data * self.Bdot2.attenuator / self.Bdot2.area) / 2
        
        #integrate dBdt to get B
        self.Bfield = scipy.integrate.cumtrapz( self.dBdt ,self.time )/1e9   #1e9 as time is in ns
        self.Bfield = np.append(self.Bfield, self.Bfield[-1] )  #adds extra index to match length of time
        
        
        #get the errors from probes - add in quadrature
        Bfield_error = np.square( self.Bdot1.noise_range * self.Bdot1.attenuator / self.Bdot1.area) \
                        + np.square( self.Bdot2.noise_range * self.Bdot2.attenuator / self.Bdot2.area)
        Bfield_error = np.sqrt( Bfield_error )
        self.Efield_error = np.abs( self.Bdot1.noise_range * self.Bdot1.attenuator) \
                        + np.abs( self.Bdot2.noise_range * self.Bdot2.attenuator)
        self.Efield_error = np.sqrt( self.Efield_error )
        
        #get the current start from the MAGPIE class
        M = MAGPIE(shotID)
        currentStart = M.currentStart
        
        #integrate to obtain B field and error
        self.Bfield = [0]
        self.Bfield_errors = [0]
        for i in range(1,len(self.dBdt)):   #yeah! manual integration!!!
            dt = (self.time[i]-self.time[i-1])/1e9
            if self.time[i]<currentStart:
                self.Bfield.append(0)
                self.Bfield_errors.append(0)
            else:
                self.Bfield.append( self.Bfield[i-1] + self.dBdt[i]*dt )
                self.Bfield_errors.append( self.Bfield_errors[i-1] + Bfield_error*dt)
        
        print("B-dot probe created")



    def readFile(self, file):
        #load Bdot data from file and create the indervidual probes
        
        #temporarily save variables here
        scope1 = None
        scope2 = None
        channel1 = None
        channel2 = None
        atten1 = None
        atten2 = None
        area1 = None
        area2 = None
        
        #load data
        for line in file:

            if "channel" in line.lower():
                if "1" in line.split('=')[0]:   #we have 2 seperate channels
                    channel1 = line.split('=')[1].strip()
                elif "2" in line.split('=')[0]:
                    channel2 = line.split('=')[1].strip()
                else:
                    channel1 = line.split('=')[1].strip()
                    channel2 = line.split('=')[1].strip()
                
            if "scope" in line.lower():
                if "1" in line.split('=')[0]:
                    scope1 = line.split('=')[1].strip()
                elif "2" in line.split('=')[0]:
                    scope2 = line.split('=')[1].strip()
                else:
                    scope1 = line.split('=')[1].strip()
                    scope2 = line.split('=')[1].strip()
                
            if "atten" in line.lower():
                if "1" in line.split('=')[0]:
                    atten1 = float(line.split('=')[1].strip())
                elif "2" in line.split('=')[0]:
                    atten2 = float(line.split('=')[1].strip())
                else:
                    atten1 = float(line.split('=')[1].strip())
                    atten2 = float(line.split('=')[1].strip())
                
            if "area" in line.lower():
                if "1" in line.split('=')[0]:
                    area1 = float(line.split('=')[1].strip())
                elif "2" in line.split('=')[0]:
                    area2 = float(line.split('=')[1].strip())
                else:
                    area1 = float(line.split('=')[1].strip())
                    area2 = float(line.split('=')[1].strip())
                    
            if "<end>" in line.lower():
                break
                
        #create Bdot probe objects
        if not None in [scope1, channel1, atten1, area1]:
            self.Bdot1 = BdotProbe( ScopeChannel(self.shotID,scope1,channel1), atten1, area1 )
        if not None in [scope2, channel2, atten2, area2]:
            self.Bdot2 = BdotProbe( ScopeChannel(self.shotID,scope2,channel2), atten2, area2 )
            
            
            
    def plot(self, plotType="B", ax=None, label=None, color=None, linestyle=None):
        if ax is None:
            fig, ax=plt.subplots()
            
        #select the correct thing to plot
        data1,label1 = None,""
        data2,label2 = None,""
        if "B" in plotType:
            data1,label1 = self.Bfield,"B field "+self.shotID
        if "E" in plotType:
            data1,label1 = self.Efield,"E field "+self.shotID
        if "fields" in plotType.lower() or "both" in plotType.lower() or "all" in plotType.lower():
            data1,label1 = self.Efield,"E field "+self.shotID
            data2,label2 = self.Bfield,"B field "+self.shotID
        
        if "raw" in plotType.lower() or "voltage" in plotType.lower():
            if "1" in plotType:
                data1,label1 = self.Bdot1.data,"Probe 1 "+self.shotID
            elif "2" in plotType:
                data1,label1 = self.Bdot2.data,"Probe 2 "+self.shotID
            else:
                data1,label1 = self.Bdot1.data,"Probe 1 "+self.shotID
                data2,label2 = self.Bdot2.data,"probe 2 "+self.shotID
        
        #apply current offset
        M = MAGPIE(self.shotID)
        plot_times = np.array(self.time) - M.currentStart
            
        #plot errors
        if "B" in plotType or "E" in plotType:
            errors = None
            if "B" in plotType:
                errors = self.Bfield_errors
            else:
                errors = [self.Efield_error]*len(data1)
            errorsMin = np.array(data1) - np.array(errors)
            errorsMax = np.array(data1) + np.array(errors)
            ax.fill_between(plot_times, errorsMin,errorsMax, facecolor=color, alpha=.5)
        
        #plot the data
        if label is not None:
            label1 = label
        if data1 is not None:
            ax.plot(plot_times, data1, label=label1,color=color,linestyle=linestyle)
        if data2 is not None:
            ax.plot(plot_times, data2, label=label2)
        
        #make graph look pretty
        plt.xlabel("Time [ns]")
        plt.title("B field for shot "+self.shotID)
        plt.xlim( [0,3000] )
        plt.legend()
        if "B" in plotType:
            plt.ylabel("B field [T]")
        if "E" in plotType:
            plt.ylabel("Electric field [V/m]")
        if "fields" in plotType.lower() or "both" in plotType.lower() or "all" in plotType.lower():
            plt.ylabel("B field [T]")
        if "raw" in plotType.lower() or "voltage" in plotType.lower():
            plt.ylabel("Voltage [V]")
        return ax