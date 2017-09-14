#Created by J. Hare
#class for handling and loading a scope channel saved on Linna

import numpy as np



class ScopeChannel:
    
    def __init__(self, shotID, scope, channel):
        self.shotID = shotID  #text e.g. smmdd_yy
        self.scope = scope
        self.channel = channel
        
        #load time series and data series
        filepath="//LINNA/scopes/scope"+self.scope+"_"+self.shotID
        self.time=np.loadtxt(filepath+"time")
        self.data=np.loadtxt(filepath+"_"+self.channel)[1:]