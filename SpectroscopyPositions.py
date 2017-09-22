#Created by T. Clayson 22/09/17
#class for finding the position of spectroscopy fibre collection volumes

import os
import matplotlib.pyplot as plt
import numpy



class SpectroscopyPositions:
    def __init__(self, shotID=None):
        
        self.fibres = []
        self.positions = [];
        
        #loop through each fibre image, plot them and have a human select the positon
        print("Select the position of the fibre on each image")
        fig, ax = plt.subplots()
        
        dataPath = "Data/"+shotID+"/"
        for fibre in range(1,15):
            filename = self.find_file(dataPath, fibre)
                
            #load and show the image
            if filename is not None:
                image = plt.imread(dataPath+filename)
                ax.set_title("Fibre "+str(fibre))
                ax.imshow( image )
                
                #get point we select
                print("Fibre "+str(fibre))
                plt.pause(0.5)
                self.fibres.append(fibre)
                self.positions.append( (plt.ginput(1))[0] )
                print(self.positions[-1])
            
                    
                    
    def find_file(self, datapath, number):
        for sf in os.listdir(datapath):
            subfile = sf.lower()
            if "fibre" in subfile:
                substring = subfile.split('fibre')[1].strip()
                substring.replace(".", " ")
                numbers = [int(s) for s in substring.split() if s.isdigit()]
                if numbers[0] == number:
                    print("Fibre image found: "+self.path)
                    return sf
        
        print("No image for fibre "+str(number)+" found")
        return None
              
                
                
    def save(self, filename):
        return
    
    
    
    def load(self, filename):
        return