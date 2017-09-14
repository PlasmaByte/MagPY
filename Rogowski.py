#Created by T. Clayson 04/08/17
#based on previous work by J. Hare

import numpy as np



class Rogowski:
    def __init__(self, scopeChannel=None, attenuator=206, height=5.8, innerRadius=18, outerRadius=24 ):
        #dimensions (height, innerRadius and outRadius) should be given in mm
        self.time = scopeChannel.time
        self.data = scopeChannel.data
        self.attenuator = attenuator
        self.multiplier = 1 / 2e-7 / height*1000 / np.log( outerRadius/innerRadius ) #multiplyer is such that I = multiplier integral V

        #remove offset from data by subtracting average in initial first few hundred points in trace
        self.data -= np.mean(self.data[0:200])
        
        #calculate current start from raw signals
        self.currentStart = 0
        noiseMax = max(self.data[0:200])*self.attenuator    #first few hundred are noise so use that to find maximum noise
        #find the point where we go above the noise more than 50 times in a row - to ensure this is the true signal
        posCount = 50   #how many positives we need
        currentStartPos = 200   #current position to check
        positives = 0;
        while self.currentStart==0:
            currentStartPos = currentStartPos+1;
            if self.data[currentStartPos]*self.attenuator >noiseMax:
                positives = positives+1
                if positives>posCount:
                    currentStartPos -= posCount
                    self.currentStart = self.time[currentStartPos]
            else:
                positives = 0