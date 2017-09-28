#Created by T. Clayson 28/07/17

import os
from SourceCode.Multiframe import Multiframe
from SourceCode.ShotData import ShotData
from SourceCode.BdotPair import BdotPair
from SourceCode.Interferometry import Interferometry
from SourceCode.MAGPIE import MAGPIE
from SourceCode.Material import Material
from SourceCode.Shock import Shock
import skimage.measure
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats



class LinerExperiment:
    def __init__(self, shotID):
        #find the shotdata folder on Linna
        self.shotID = shotID
        self.shotData = ShotData(shotID)
        path = "Data/"+self.shotID
        
        #variables with defaults
        self.dataPath = "Data/"+shotID+"/"
        self.linerMaterial = "stainless steel"
        self.linerThickness = 100;
        
        #load up MAGPIE class
        self.MAGPIE = MAGPIE(shotID)
        
        #load subfiles
        self.shock = []
        self.multiframe = []
        self.bdotPairs = []
        self.interferometry = []
        for subfile in os.listdir(path):
            if "shock dynamics" in subfile.lower():
                self.shock.append( Shock(shotID, fileName=subfile) )
            if "multiframe" in subfile.lower():
                self.multiframe.append( Multiframe(shotID, fileName=subfile) )

        #find liner experiment file and load its data
        filename = self.dataPath+"Liner Experiment"
        if not os.path.isfile(filename):    #check we have the file
            print("No file found: "+filename)
            return
            
        #open shot file and read line by line to load all data
        gas_element, gas_pressure = "Ar", 24
        with open(filename) as file:
            for l in file:
                line = l.lower()

                if "liner material" in line:
                    self.linerMaterial = line.split('=')[1].strip()
                
                if "liner thickness" in line:
                    self.linerThickness = float(line.split('=')[1].strip())
                    
                if "gas fill" in line:
                    gas_element = line.split('=')[1].strip()
                    
                if "gas pressure" in line:
                    gas_pressure = float(line.split('=')[1].strip())
                    
                if "<interferometry>" in line:    #setup interferometry
                    print("load Interferometry")
                    self.interferometry.append( Interferometry(file=file, shotData=self.shotData) )
                
                if "<bdot pair>" in line:    #setup Bdot pair
                    print("load Bdot")
                    self.bdotPairs.append( BdotPair(file=file, shotID=shotID) )
                      
        #setup the gas fill
        self.gas_fill = Material(gas_element, pressure = gas_pressure/1000)
        
        
        
    def primary_shock(self):
        if len(self.shock)==1:
            return self.shock[0]
        
        new_shock = Shock(self.shotID)
        new_shock.clear()
        new_shock.append(self.shock[0],multiplier=-1)
        new_shock.append(self.shock[1],multiplier=1)
        new_shock.calculate_velocity()
        return new_shock
    
    
                    
    def getInterferometry(self, wavelength=10):  #easy method for finding interferometry of specific wavelengths
        for inter in self.interferometry:
            if inter.wavelength==wavelength:
                return inter