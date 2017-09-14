#Created by T. Clayson 25/08/17
#class for analyising two interferometry data sets
#stores a map of both electron density and neutral density

# maths found in B. V. Weber, S. F. Fulghum
# "A high sensitivity two-color interferometer for pulsed power plasmas"
# RSI 68 (2) (1996)

from SourceCode.Interferometry import Interferometry
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage

class DualInterferometry:
    def __init__(self, interferometry1 , interferometry2):
        self.interferometry1 = interferometry1 #interferometry objects
        self.interferometry2 = interferometry2
        
        self.electronMap = None
        self.neutralsMap = None
        self.extent = [0]*4
        


    def process(self):
        #first determin the size of the final map - in mm
        extent1 = self.interferometry1.getImageExtent()
        extent2 = self.interferometry2.getImageExtent()
        self.extent[0] = min(extent1[0],extent2[0])
        self.extent[1] = max(extent1[1],extent2[1])
        self.extent[2] = min(extent1[2],extent2[2])
        self.extent[3] = max(extent1[3],extent2[3])
        
        #make both maps be as large as the region we are covering
        #density = 100 pixels per mm
        scale = 100
        xsize = int((self.extent[3] - self.extent[2])*scale)
        ysize = int((self.extent[1] - self.extent[0])*scale)
        self.electronMap = np.zeros( (xsize,ysize) )
        self.neutralsMap = np.zeros( (xsize,ysize) )
        map1 = np.zeros( (xsize,ysize) )
        map2 = np.zeros( (xsize,ysize) )
        
        #set the regions of map1 and map2 which we know
        pixels1 = [0]*4 # creates array to store pixel positions of min/max x/y in the final image
        pixels1[0] = int((extent1[0]-self.extent[0])*scale)
        pixels1[1] = int((extent1[1]-self.extent[0])*scale)
        pixels1[2] = int((extent1[2]-self.extent[2])*scale)
        pixels1[3] = int((extent1[3]-self.extent[2])*scale)
        resize = float(pixels1[3]-pixels1[2]) / float(self.interferometry1.getImage("final").shape[0])
        map1sub = scipy.ndimage.zoom( self.interferometry1.getImage("final"), resize , order=3)
        map1[ pixels1[2]:pixels1[3] , pixels1[0]:pixels1[1] ] = map1sub

        pixels2 = [0]*4
        pixels2[0] = int((extent2[0]-self.extent[0])*scale)
        pixels2[1] = int((extent2[1]-self.extent[0])*scale)
        pixels2[2] = int((extent2[2]-self.extent[2])*scale)
        pixels2[3] = int((extent2[3]-self.extent[2])*scale)
        resize = float(pixels2[3]-pixels2[2]) / float(self.interferometry2.getImage("final").shape[0])
        map2sub = scipy.ndimage.zoom( self.interferometry2.getImage("final"), resize , order=3)
        map2[ pixels2[2]:pixels2[3] , pixels2[0]:pixels2[1] ] = map2sub

        #remove offset and <0 values
        map1 = map1 -1.62e17
        map1 = np.clip(map1, 0, 1e20)
        map2 = map2 -9.42e17
        map2 = np.clip(map2, 0, 1e20)

        #outputs of magic are neL so we need to convert them to phase difference (1e-7 to convert wavelength to cm)
        map1 = -map1 * 2.82e-13 * (self.interferometry1.wavelength*1e-7)
        map2 = -map2 * 2.82e-13 * (self.interferometry2.wavelength*1e-7)
        
        fig, ax = plt.subplots()
        ax.imshow(map1)
        fig, ax = plt.subplots()
        ax.imshow(map2)

        #do maths in paper with map1 and map2 to get electron and neutral densities
        print("Combining interferomgrams")
        wavelength1 = self.interferometry1.wavelength * 1e-7 #in cm
        wavelength2 = self.interferometry2.wavelength * 1e-7
        electronDenominator = wavelength1*wavelength1 + wavelength2*wavelength2
        neutralsDenominator = wavelength1/wavelength2 + wavelength2/wavelength1
        for x in range(0,map2.shape[0]):
            for y in range(0,map2.shape[1]):
                self.electronMap[x,y] = (map2[x,y]*wavelength2 - map1[x,y]*wavelength1) / electronDenominator
                self.neutralsMap[x,y] = (map2[x,y]*wavelength1 - map1[x,y]*wavelength2) / neutralsDenominator
            if x%10==0:
                print( str(x*100/map2.shape[0])+"%" )
                
        # sort out constants
        self.electronMap = self.electronMap / 2.82e-15
        self.neutralsMap = self.neutralsMap / 2 / np.pi / 0.0002820 #assumes argons index of refraction is 1.0002820
        
        
        
    def plot(self, plotType="electron" , crop=None):
        if "electron" in plotType or "e-" in plotType:
            image = self.electronMap
        if "neutral" in plotType:
            image = self.neutralsMap

        fig, ax = plt.subplots()
        extent = self.extent

        #crop image to a smaller region if necessary
        if crop is not None:
            xstart = (int)((crop[0]-self.offset[0]) * self.scale)
            xstop = (int)((crop[1]-self.offset[0]) * self.scale)
            ystart = (int)((crop[2]-self.offset[1]) * self.scale)
            ystop = (int)((crop[3]-self.offset[1]) * self.scale)
            print([xstart,xstop,ystart,ystop])
            if len(image.shape)>2:
                image = image[ystart:ystop,xstart:xstop,:]
            else:
                image = image[ystart:ystop,xstart:xstop]
            extent = crop

        #plot image
        cax = ax.imshow( image , extent=extent)
        #make it look nice
        ax.axis('on')
        plt.xlabel('position [mm]')
        plt.ylabel('position [mm]')
        fig.colorbar(cax, shrink=0.7)
        return ax