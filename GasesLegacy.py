#Created by T. Clayson 01/09/17
#class for handling standard gas calculations

#requires the periodictable Python package: https://pypi.python.org/pypi/periodictable
#to instal copy the following into your prompt: conda install -c conda-forge periodictable



class Gases:
            
    def __init__(self, gas="He", density=0.0, pressure=0.0, temperature=300):
        #density in kg/m^3 or mg/cc
        #pressure in bar
        #temperature in Kelvin
        self.gas = gas
        
        #setup the gas elements
        self.elements = []
        if gas is not None:
            self.elements = self.ImportElement(gas)
        
        
        self.temperature = temperature

        #calculate the number density of the gas in /m^3
        if density>0:
            self.density = density / ( self.Weight() * 1.660539040e-27 )
        else:
            #calculate the number density from pressure
            self.density = pressure*1e5 / 1.38064852e-23 / temperature
            
        
        
    def ImportElement(self, gas="He"):
        gas = gas.lower()
        if gas=="h" or gas=="hydrogen":
            from periodictable import H
            return [H,H]
        elif gas=="he" or gas=="helium":
            from periodictable import He
            return [He]
        elif gas=="n" or gas=="nitrogen":
            from periodictable import N
            return [N,N]
        elif gas=="o" or gas=="oxygen":
            from periodictable import O
            return [O,O]
        elif gas=="f" or gas=="fluorine":
            from periodictable import F
            return [F,F]
        elif gas=="ne" or gas=="neon":
            from periodictable import Ne
            return [Ne]
        elif gas=="cl" or gas=="chlorine":
            from periodictable import Cl
            return [Cl,Cl]
        elif gas=="ar" or gas=="argon":
            from periodictable import Ar
            return [Ar]
        elif gas=="kr" or gas=="krypton":
            from periodictable import Kr
            return [Kr]
        elif gas=="xe" or gas=="xenon":
            from periodictable import Xe
            return [Xe]
        elif gas=="rn" or gas=="radon":
            from periodictable import Rn
            return [Rn]
        
        
        
    def Weight(self):
        #returns the mass in atomic units
        result = 0
        for e in self.elements:
            result += e.mass
        return result
    
    
    
    def MassDensity(self):
        #returns in kg/m^3 = mg/cc
        return self.density * self.Weight() * 1.660539040e-27
    
    
    
    def Pressure(self):
        #assume ideal gas - returns in bar
        return self.density * 1.38064852e-23 * temperature / 1e5