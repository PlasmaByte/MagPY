#Created by T. Clayson 19/09/17
#class for looking up atomic data

import numpy
import os.path

def is_element(label="H"):
    #load the data searching for the row corresponding to the letter, name or number
    dataFile = "SourceCode/ElementData"
    if os.path.exists(dataFile) is False:
        print("AHHH! ElementData file not found!")
        return
    
    with open(dataFile) as file:
        for line in file:
            contents = line.split('\t')
            if contents[0].lower()==label or contents[1].lower()==label or int(contents[2])==label:
                return True
    return False



class Element:
    def __init__(self, label="H"):
        
        self.symbol = None
        self.name = None
        self.atomic_number = None
        self.atomic_mass = None
        
        #load the data searching for the row corresponding to the letter, name or number
        dataFile = "SourceCode/ElementData"
        if os.path.exists(dataFile) is False:
            print("AHHH! ElementData file not found!")
            return
        
        with open(dataFile) as file:
            for line in file:
                if "Symbol" not in line:
                    contents = line.split('\t')
                    if len(contents)>2:
                        if contents[0].lower()==label.lower() or contents[1].lower()==label.lower() or int(contents[2])==label:
                            self.symbol = contents[0]
                            self.name = contents[1]
                            self.atomic_number = int(contents[2])
                            self.atomic_mass = float(contents[3])
                            print(self.name+" data loaded")
                            break
        if self.name is None:
            print("No elemental data found for "+label)
                
                
    def protons(self):
        return self.atomic_number
        
    def neutrons(self):
        return self.atomic_mass - self.atomic_number

    def ionization(self, temperature ):
        #temperature in eV
        #aproximation taken from P. Drake book
        ion = numpy.sqrt(20*temperature/1000)
        return min( self.atomic_number,ion)