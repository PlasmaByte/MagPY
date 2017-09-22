#Created by T. Clayson 19/09/17
#class for looking up atomic data

import numpy
import matplotlib.pyplot as plt

class Element:
    def __init__(self, symbol="H"):
        self.symbol = symbol
        return
        
    def name(self):
        dic = {
            'H' : "Hydrogen",
            'He' : "Helium",
            'C' : "Carbon",
            'N' : "Nitrogen",
            'Ne' : "Neon",
            'Ar' : "Argon",
            'Kr' : "Krypton",
            'Xe' : "Xenon",
            'Rn' : "Radon",
        }
        return dic.setdefault(self.symbol, "None")
    
    def atomic_mass(self):
        #https://en.wikipedia.org/wiki/Standard_atomic_weight
        dic = {
            'H' : 1.008,
            'He' : 4.0026,
            'C' : 12.011,
            'N' : 14.0067,
            'Ne' : 20.1797,
            'Ar' : 39.948,
            'Kr' : 83.798,
            'Xe' : 131.29,
            'Rn' : 222,
        }
        return dic.setdefault(self.symbol, 1)
    
    def atomic_number(self):
        dic = {
            'H' : 1,
            'He' : 2,
            'C' : 6,
            'N' : 7,
            'Ne' : 10,
            'Ar' : 18,
            'Kr' : 36,
            'Xe' : 54,
            'Rn' : 86,
        }
        return dic.setdefault(self.symbol, 1)

    def ionization(self, temperature ):
        #temperature in eV
        #aproximation taken from P. Drake book
        ion = numpy.sqrt(20*temperature/1000)
        return min( self.atomic_number() ,ion)