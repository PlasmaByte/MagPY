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
        
        #characterise nosie = first 1000 points
        noiseValues = 1000
        self.currentStart = 0
        threshold = max(self.data[0:noiseValues])*self.attenuator    #first few hundred are noise so use that to find maximum noise
        self.noise_range = (max(self.data[0:noiseValues]) - min(self.data[0:noiseValues]))/2
        
        #find the point where we go above zero more than 50 times in a row
        #to ensure this is the true signal
        posCount = 50   #how many positives we need
        currentStartPos = noiseValues   #current position to check
        positives = 0;
        while self.currentStart==0:
            currentStartPos += 1;
            if self.data[currentStartPos]*self.attenuator > threshold:
                positives = positives+1
                if positives>posCount:
                    currentStartPos -= posCount
                    self.currentStart = self.time[currentStartPos]
                    break
            else:
                positives = 0
        
        #calculate the error by taking the max of the noise and seeing how
        #long till our signal passes that value
        noiseCrossTime = 0
        while currentStartPos<len(self.data):
            if self.data[currentStartPos]*self.attenuator >threshold+self.noise_range*self.attenuator:
                noiseCrossTime = self.time[currentStartPos]
                break
            currentStartPos += 1;
            
        self.currentStart_error = noiseCrossTime - self.currentStart