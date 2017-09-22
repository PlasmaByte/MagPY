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