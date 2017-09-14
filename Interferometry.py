#Created by T. Clayson 24/08/17
#class for handling interferometry data

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from scipy.ndimage.interpolation import shift
import skimage.measure
import scipy.io
import os.path
from copy import deepcopy



class Interferometry:
    def __init__(self, file=None, shotData=None):
        #defaults
        self.shotData = shotData
        self.wavelength = 532   #nm
        self.scale = 90         #pixels/mm
        self.angle = 0          #degrees
        self.offset = (0,0)     #mm
        self.flipLR = False
        self.flipUD = False
        
        self.refImagePath = ""    #stores paths of these images for later loading
        self.dataImagePath = ""
        self.finalImagePath = ""
        
        self.refImage = None    #stores the actual images after loading them
        self.dataImage = None
        self.finalImage = None

        if file is not None:
            self.readData(file)

            
            
    def readData(self,file):
        #read data from file till we reach the next import keyword
        for l in file:
            line = l.lower()

            if ("data" in line or "raw" in line or "shot" in line) and "file" in line:
                if "/" in line:
                    self.dataImagePath = line.split('=')[1].strip()
                else:
                    self.dataImagePath = "Data/"+self.shotData.shotID+"/"+line.split('=')[1].strip()
                
            if ("ref" in line or "back" in line) and "file" in line:
                if "/" in line:
                    self.refImagePath = line.split('=')[1].strip()
                else:
                    self.refImagePath = "Data/"+self.shotData.shotID+"/"+line.split('=')[1].strip()
                
            if ("proc" in line or "final" in line) and "file" in line:
                if "/" in line:
                    self.finalImagePath = line.split('=')[1].strip()
                else:
                    self.finalImagePath = "Data/"+self.shotData.shotID+"/"+line.split('=')[1].strip()
                
            if "wavelength" in line:
                self.wavelength = float(line.split('=')[1].strip() )
                
            if "scale" in line:
                self.scale = float(line.split('=')[1].strip() )
                
            if "angle" in line:
                self.angle = float(line.split('=')[1].strip() )
                
            if "offset" in line:
                temp = line.split('=')[1].strip() 
                self.offset = ( float(temp.split(',')[0]), float(temp.split(',')[1]) )
                
            if "fliplr" in line:
                self.flipLR = True
                
            if "flipud" in line:
                self.flipUD = True
            
            if "<end>" in line:
                break
  
                        
                        
    def getImage(self, imageType="shot"):
        #check if the image exists, if not load/create it
        if "back" in imageType or "ref" in imageType:
            if self.refImage is None:
                print("Opening image at "+self.refImagePath)
                #load image if we don't have it
                self.refImage = self.CorrectImage(plt.imread(self.refImagePath))   #load image if we don't have it
            return self.refImage
                
        if "data" in imageType or "raw" in imageType or "shot" in imageType:
            if self.dataImage is None:
                print("Opening image at "+self.dataImagePath)
                self.dataImage = self.CorrectImage(plt.imread(self.dataImagePath))   #load image if we don't have it
            return self.dataImage

        if "proc" in imageType or "final" in imageType:
            if self.finalImage is None:
                print("Opening image at "+self.finalImagePath)
                #loads a matlab file output from Magic
                X = scipy.io.loadmat(self.finalImagePath)
                X = np.nan_to_num(X['Density'])
                self.finalImage = self.CorrectImage(X)
            return self.finalImage
    
        
        
    def CorrectImage(self, image):
        if self.flipLR:
            image = np.fliplr(image)
        if self.flipUD:
            image = np.flipud(image)
        image = rotate( image, self.angle ) # apply rotation
        return image
        
        
    
    def getImageExtent(self, plotType="final"):
        #returns the image size in a 4 element list [xmin,xmax,ymin,ymax] in mm
        image = self.getImage(imageType=plotType)
        xsize = image.shape[1] / self.scale
        ysize = image.shape[0] / self.scale
        return [ self.offset[0],self.offset[0]+xsize, self.offset[1],self.offset[1]+ysize ]
    
    
    
    def forceToZero(self, region):
        #region = [xstart,xstop,ystart,ystop] in mm
        image = self.getImage(imageType="final")
        #get average of region
        region = self.convertToPixel(region)
        coffset = np.mean(np.mean( image[ region[3]:region[2], region[0]:region[1] ] ))
        image = image - coffset
        #remove any less than zero points
        image = np.clip(image, 0, 1e25)
        self.finalImage = image
        return image
    
    
    
    def convertToPixel(self, value):
        image = self.getImage(imageType="final")
        yheight = image.shape[0]
        if len(value)==2:   # point
            value[0] = int((value[0]-self.offset[0])*self.scale)
            value[1] = yheight-int((value[1]-self.offset[1])*self.scale)
        if len(value)==4:   # area
            value[0] = int((value[0]-self.offset[0])*self.scale)
            value[1] = int((value[1]-self.offset[0])*self.scale)
            value[2] = yheight-int((value[2]-self.offset[1])*self.scale)
            value[3] = yheight-int((value[3]-self.offset[1])*self.scale)
        return value
    
    
    
    def getLineout(self, start, stop, thickness=1 ):
        image = self.getImage(imageType="final")
        start = self.convertToPixel(start)
        start.reverse()
        stop = self.convertToPixel(stop)
        stop.reverse()
        line = skimage.measure.profile_line(image, start,stop, linewidth=thickness*self.scale )
        return line
        

                        
    def plot(self, plotType="shot", crop=None, vmin=None, vmax=None, title=None):
        image = self.getImage(imageType=plotType)

        fig, ax = plt.subplots()
        extent = self.getImageExtent(plotType)
        
        #crop image to a smaller region if necessary
        if crop is not None:
            extent = deepcopy(crop)
            crop = self.convertToPixel(crop)
            if len(image.shape)>2:
                image = image[crop[3]:crop[2],crop[0]:crop[1],:]
            else:
                image = image[crop[3]:crop[2],crop[0]:crop[1]]

        #plot image
        #add colorbar if plotting final processed images
        if "proc" in plotType.lower() or "final" in plotType.lower():
            magnitude = 1e18
            if vmin is not None:
                vmin = vmin/magnitude
            if vmax is not None:
                vmax = vmax/magnitude
            cax = ax.imshow( image/magnitude , extent=extent, cmap="inferno", vmin=vmin, vmax=vmax)
            cbar = fig.colorbar(cax, shrink=0.7)
            cbar.set_label('Integrated electron density $n_e$ [$cm^2$]', rotation=270, labelpad=20)
            cbar.ax.text(-0.25, 1, r'$\times$10$^{18}$', va='bottom', ha='left')
        else:
            cax = ax.imshow( image , extent=extent)
        
        #make it look nice
        ax.axis('on')
        if title is None:
            ax.set_title(self.shotData.shotName)
        else:
            title = title.replace("*", self.shotData.shotName)  #* in title is replaced by shotname
            ax.set_title(title)
        plt.xlabel('Position [mm]')
        plt.ylabel('Position [mm]')
        return ax