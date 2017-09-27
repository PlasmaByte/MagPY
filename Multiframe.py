#Created by T. Clayson 28/07/17
#class for loading 12 frame images
#based on previous work by J. Hare

import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from scipy.ndimage.interpolation import shift
from copy import deepcopy
from SourceCode.ShotData import ShotData
from scipy import stats



class Multiframe:
    def __init__(self, shotID="", shotData=None, fileName=None):
        #class variable defaults
        self.shotID = shotID
        self.frames = 12
        self.startTime = 0      #ns
        self.frameTimes = []    #ns
        self.interFrame = 100   #ns
        self.exposure = 0       #ns
        self.scale = 90         #pixels/mm
        self.angle = 0          #degrees
        self.offset = (0,0)     #mm
        self.flipLR = False
        self.flipUD = False
        
        if shotData is None:    #find the shotdata folder on Linna
            self.shotData = ShotData(shotID)

        self.relativeOffsets = []
        self.intensities = []
        self.shotImagesPath = []
        self.backImagesPath = []

        if fileName is None:
            #find file
            self.fileName = None
            for subfile in os.listdir("Data/"+self.shotID):
                if "multiframe" in subfile.lower():
                    self.fileName = subfile
                    print("Multiframe file found: "+self.fileName)
                    
        self.readData()

        #complete frame times with equal interfram
        if len(self.frameTimes)==0:
            self.frameTimes.append(self.startTime)
        while len(self.frameTimes)<self.frames:
            self.frameTimes.append( self.frameTimes[-1]+self.interFrame )

        #get the image paths
        self.find_images()
        
        #creates arrays for storing images
        self.shotImages = [None]*self.frames
        self.backImages = [None]*self.frames
        self.shotImagesRaw = [None]*self.frames #stores unrotated and unshifted images
        self.backImagesRaw = [None]*self.frames #stores unrotated and unshifted images
        
            
            
    def readData(self):
        path = "Data/"+self.shotID
        
        if self.fileName is None:
            print("No multiframe file found")
            return
        
        with open(path+"/"+self.fileName) as file:
            #read the file line by line
            for l in file:
                line = l.lower()
                if "frames" in line:
                    self.frames = int(line.split('=')[1].strip())
                if "inter frame" in line:
                    self.interFrame = float(line.split('=')[1].strip() )
                if "start time" in line:
                    self.startTime = float(line.split('=')[1].strip() )
                if "exposure" in line:
                    self.exposure = float(line.split('=')[1].strip() )
                if "scale" in line:
                    self.scale = float(line.split('=')[1].strip() )
                if "angle" in line:
                    self.angle = float(line.split('=')[1].strip() )
                if "offset" in line:
                    temp = line.split('=')[1].strip() 
                    self.offset = ( float(temp.split(',')[0]), float(temp.split(',')[1]) )
                if "frame times" in line:
                    #load specific frame times seperated by commas
                    subline = line.split('=')[1].strip()
                    comma_seperated = subline.split(',')
                    for c in comma_seperated:
                        self.frameTimes.append( float(c.strip()) )
                if "fliplr" in line:
                    self.flipLR = True;
                if "flipud" in line:
                    self.flipUD = True;
                    
                if "<end>" in line.lower():
                    break
            
                #get frame relative offsets
                contents = line.split('\t')
                if len(contents)==4:
                    if "frame" not in contents[0]:
                        self.relativeOffsets.append( np.array([ float(contents[1]) , float(contents[2]) ]) )
                        self.intensities.append( float(contents[3]) )
                
                
                
    def find_images(self):
        #finds the images using the shotData class
        self.folder = ""
        for subfolder in os.listdir(self.shotData.path):
            if ("fast frame" in subfolder.lower() or "fast-frame" in subfolder.lower()
                or "12 frame" in subfolder.lower() or "12-frame" in subfolder.lower()
                or "multiframe" in subfolder.lower()) :
                self.folder = self.shotData.path+"/"+subfolder
        
        #if we can't find something explicitly labelled just take any folder!
        if self.folder == "":
            for subfolder in os.listdir(self.shotData.path):
                if os.path.isdir(self.shotData.path+"/"+subfolder):
                    self.folder = self.shotData.path+"/"+subfolder
                
        if self.folder == "":
            print("No multiframe folder found")
            return;
        else:
            print("Multiframe folder found: "+self.folder)
            
        #we don't load the images at the moment and instead just record the file locations
            
        #find the shot folder and images - don't load as too slow
        self.shotImagesPath = []
        for subfolder in os.listdir(self.folder):
            if "shot" in subfolder.lower():
                self.findImages(self.folder+"/"+subfolder,self.shotImagesPath)
                
        #find the shot folder and images - don't load as too slow
        self.backImagesPath = []
        for subfolder in os.listdir(self.folder):
            if "back" in subfolder.lower():
                self.findImages(self.folder+"/"+subfolder,self.backImagesPath)
        
        
                
    def findImages(self,path,array):
        fileExtension = ".tif"
        for imagefile in os.listdir(path):
            for x in range(1, self.frames+1): #for each file test if it is the image we want
                if x<10:
                    if "00"+str(x)+fileExtension in imagefile:
                        array.append( path+"/"+imagefile)
                else:
                    if "0"+str(x)+fileExtension in imagefile:
                        array.append(path+"/"+imagefile)
                        
                        
                        
    def getImage(self, frame, imageType="shot"):
        #check if the image exists, if not load/create it
        if "back" in imageType:
            if "raw" in imageType:  #raw background images
                if self.backImagesRaw[frame-1] is None:
                    self.backImagesRaw[frame-1] = plt.imread(self.backImagesPath[frame-1])  #load image if we don't have it
                return self.backImagesRaw[frame-1]
            else:   #corrected background images
                if self.backImages[frame-1] is None:
                    self.correctFrame(frame,imageType)
                return self.backImages[frame-1]
        else:
            if "raw" in imageType:  #raw shot images
                if self.shotImagesRaw[frame-1] is None:
                    self.shotImagesRaw[frame-1] = plt.imread(self.shotImagesPath[frame-1])  #load image if we don't have it
                return self.shotImagesRaw[frame-1]
            else:   #corrected shot images
                if self.shotImages[frame-1] is None:
                    return self.correctFrame(frame,imageType)
                return self.shotImages[frame-1]



    def correctFrame(self, frame, imageType="shot"):
        image = None
        
        #load the correct image
        if "back" in imageType:
            if self.backImagesRaw[frame-1] is None:
                self.backImagesRaw[frame-1] = plt.imread(self.backImagesPath[frame-1])
            image = self.backImagesRaw[frame-1]
        else:
            if self.shotImagesRaw[frame-1] is None:
                self.shotImagesRaw[frame-1] = plt.imread(self.shotImagesPath[frame-1])
            image = self.shotImagesRaw[frame-1]

        image = rotate( image, self.angle )     #apply rotation
        #offset = ( self.relativeOffsets(frame)[0]+self.offset[0]*self.scale , self.relativeOffsets(frame)[1]+self.offset[1]*self.scale )
        
        #apply flips
        if self.flipLR is True:
            image = np.fliplr(image)
        if self.flipUD is True:
            image = np.flipud(image)
        
        offset = -self.getRelativeOffset(frame)
        offset = np.fliplr([offset])[0]
        image = shift( image, -offset*self.scale )  #apply relative offsets
        #save the new image
        if "back" in imageType:
            self.backImages[frame-1] = image
        else:
            self.shotImages[frame-1] = image
        
        return image
    
    
    
    def getImageExtent(self, plotType="final"):
        #returns the image size in a 4 element list [xmin,xmax,ymin,ymax] in mm
        image = self.getImage(1,imageType=plotType)
        xsize = image.shape[1] / self.scale
        ysize = image.shape[0] / self.scale
        return [ self.offset[0],self.offset[0]+xsize, self.offset[1],self.offset[1]+ysize ]
    
    
    
    def convertToPixel(self, value):
        image = self.getImage(1,imageType="shot")
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
        

                        
    def plot(self, frame=1, plotType="shot", crop=None, clim=None, vmin=None, 
             vmax=None, normalize=True):
        
        image = None
        if normalize is True:
            image = self.normalized(frame, imageType=plotType)
        else:
            image = self.getImage(frame, imageType=plotType)
        
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
        ax.imshow( image , cmap='afmhot', clim=clim, vmin=vmin, vmax=vmax, extent=extent )
        #make it look nice
        ax.axis('on')
        ax.set_title('time = '+str(self.frameTimes[frame-1])+' ns', fontsize=22)
        plt.xlabel('position [mm]')
        plt.ylabel('position [mm]')
        return ax
    
    
    
    def normalized(self, frame, imageType="shot"):
        #normalizes the shot images
        temp = self.getRelativeOffset(frame)    #call to load the intensities
        imag = self.getImage(frame,imageType=imageType) / self.intensities[frame-1]
        return imag
    
    
    
    def combinationPlot(self, plotType="shot", crop=None, clim=None, vmin=None, vmax=None, rows=0):
        if rows==0:
            rows = int(np.floor(np.sqrt(self.frames)))
        collums = int(np.ceil( self.frames/rows ))
        fig, ax = plt.subplots(rows,collums)
        
        extent = self.getImageExtent(plotType)
        if crop is not None:
            A = deepcopy(crop)
            cropPixels = self.convertToPixel(A)
        
        for i in range(0,self.frames):
            subax = ax[ int(i/collums), i%collums ]
            frame = i+1
            image = self.normalized(frame, imageType=plotType)
            
            #crop image to a smaller region if necessary
            if crop is not None:
                extent = deepcopy(crop)
                if len(image.shape)>2:
                    image = image[cropPixels[3]:cropPixels[2],cropPixels[0]:cropPixels[1],:]
                else:
                    image = image[cropPixels[3]:cropPixels[2],cropPixels[0]:cropPixels[1]]
            
            subax.imshow( image , cmap='afmhot', clim=clim, vmin=vmin, vmax=vmax, extent=extent )
            #make it look nice
            subax.axis('on')
            subax.set_title(str( int(self.frameTimes[frame-1]) )+' ns')
            
        #set labels correctly
        for x in range(0,collums):
            for y in range(0,rows):
                if x==0:
                    ax[y,x].set_ylabel("Position [mm]")
                else:
                    ax[y,x].set_ylabel("")
                if y==rows-1:
                    ax[y,x].set_xlabel("Position [mm]")
                else:
                    ax[y,x].set_xlabel("")
        
        return ax
        
        
        
    def getRelativeOffset(self, frame):
        #returns offset in mm
        if len(self.relativeOffsets)>0:    #return the correct offset if already loaded
            return self.relativeOffsets[frame-1]

        #load the relative offset file
        fileName = None
        
        path = "Data/"+self.shotData.shotID
        for subfile in os.listdir(path):    #search for file
            if "relative offsets" in subfile.lower():
                fileName = path+"/"+subfile
        if fileName is None: #default file
            fileName = "Data/Multiframe Relative Offsets"
            print("No relative offsets found - using default")
        
        #load the file and save relative offsets
        self.relativeOffsets = []
        self.intensities = []
        with open(fileName) as file:
            for line in file:
                contents = line.split('\t')
                if len(contents)>1:
                    if "Frame" not in contents[0]:
                        self.relativeOffsets.append( np.array([ float(contents[1]) , float(contents[2]) ]) )
                        self.intensities.append( float(contents[3]) )
                    
        return self.relativeOffsets[frame-1]
#                
#        #offset in pixels - calibrated with shot s0209_17
#        #likely to vary with every shot series
#        dic = {
#            1 : (7.1618,-6.605),
#            2 : (9.3654,-5.1506),
#            3 : (-28.0962,-12.4222),
#            4 : (14.8744,-5.8778),
#            5 : (-30.2998,-5.1506),
#            6 : (19.2817,-10.2407),
#            7 : (17.0781,-5.1506),
#            8 : (18.1799,9.3924),
#            9 : (-29.198,12.301),
#            10 : (13.7726,11.5738),
#            11 : (-28.0962,7.2109),
#            12 : (15.9762,10.1195)
#        }
#        return dic.setdefault(frame, (0.0,0.0) )
        
       
        
    def determinRelativeOffsets(self):
        print("Select the same point on each image to determin relative offsets")
        points = []
        fig, ax = plt.subplots()
        
        #self.plot(frame=1, plotType="background raw", ax=ax) #plot first image
        #ax.set_title("frame 1")
        #get the coordinates of a point from each multiframe image
        for i in range(0,self.frames):
            self.plot(frame=i+1, plotType="background raw", ax=ax)
            ax.set_title("frame "+str(i+1))
            print("frame "+str(i+1))
            plt.pause(0.5)
            points.append( (plt.ginput(1))[0] )
            print(points[-1])
            
        #subtract averages to ensure smallest offsets
        averageX,averageY = 0,0
        for i in range(0,self.frames):
            averageX += (points[i])[0]
            averageY += (points[i])[1]
        averageX /= float(self.frames)
        averageY /= float(self.frames)
        for i in range(0,self.frames):
            points[i] = ( (points[i])[0]-averageX , (points[i])[1]-averageY )
            
        #store average intensity so we can normalise these images later
        intensities = []
        for i in range(0,self.frames):
            imag = self.getImage(i,imageType="background raw")
            intensities.append( np.mean(imag) )
            
        #save outputs to file
        filename = "Data/"+self.shotData.shotID+"/Multiframe Relative Offsets"
        print("Writing file "+filename)
        with open(filename, 'w') as file:   #writes file
            file.write( "Multiframe relative offsets based on background images from shot "+self.shotData.shotID+"\n" )
            
            file.write( "\nFrame\tPixels X\tPixels Y\tIntensity\n" )
            for i in range(0,self.frames):
                file.write( str(i)+"\t"+str((points[i])[0])+"\t"+str((points[i])[1])+"\t"+str(intensities[i])+"\n" )
                
                
                
    def lineout(self, frame, line, thickness=0.1, demo=False):
        import skimage.measure
        #line is a 4 element array [x1,x2,y1,y2] in mm
        line_pix = self.convertToPixel(deepcopy(line))
        image = self.getImage(frame)
        thickness *= self.scale #convert to pixels
        lineout = skimage.measure.profile_line( image, (line_pix[2],line_pix[0]),
                                               (line_pix[3],line_pix[1]), linewidth=thickness )
        
        if demo is True:    #if in demo mode plot the image and draw on the lineout
            ax = self.plot(frame)
            ax.plot( [line[0], line[1]], [line[2], line[3]], 'w--' )  # plot lines
        
        return lineout
        