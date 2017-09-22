#Created by T. Clayson 22/09/17
#class for loading and processing spectroscopy data

import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from scipy.ndimage.interpolation import shift
from copy import deepcopy



class Spectroscopy:
    def __init__(self, shotID):
        
        #class variable defaults
        self.fibres = 14
        self.exposure = 4   #ns
        self.time = 500     #ns
        self.gain = 120
        self.grating = 300  #lines/mm
        self.central_wavelength = 400   #nm
        
        #find details file and load its data
        self.dataPath = "Data/"+shotID+"/"
        filename = self.dataPath+"Spectroscopy"
        if not os.path.isfile(filename):    #check we have the file
            print("No spectroscopy file found: "+filename)
            return
        
        #open shot file and read line by line to load all data
        with open(filename) as file:
            for l in file:
                line = l.lower()
                if "fibres" in line:
                    self.fibres = line.split('=')[1].strip()
                if "exposure" in line:
                    self.exposure = line.split('=')[1].strip()
                if "time" in line:
                    self.time = line.split('=')[1].strip()
                if "gain" in line:
                    self.gain = line.split('=')[1].strip()
                if "grating" in line:
                    self.grating = line.split('=')[1].strip()
                if "wavelength" in line:
                    self.central_wavelength = line.split('=')[1].strip()