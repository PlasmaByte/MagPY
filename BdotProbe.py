#Created by T. Clayson 07/08/17

import numpy as np



class BdotProbe:
    def __init__(self, scopeChannel=None, attenuator=206, area=4.1):
        #dimensions (height, innerRadius and outRadius) should be given in mm
        self.time = scopeChannel.time
        self.data = scopeChannel.data
        noiseValues = 1000
        self.noise_range = ( max(self.data[0:noiseValues]) - min(self.data[0:noiseValues]) )/2
        self.attenuator = attenuator
        self.area = area/1e6 #converts to m^2

        #remove offset from data by subtracting average in initial first few hundred points in trace
        self.data -= np.mean(self.data[0:200])