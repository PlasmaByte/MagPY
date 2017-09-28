#Created by T. Clayson 27/09/17
#class for simulating a material (solid, liquid, gas or plasma)

from SourceCode.Element import Element
from SourceCode.Constants import Constants



class Material:
    #generic material class, can use lookup data or be made of multiple elements
            
    def __init__(self, name="He", number_density=0.0, mass_density=0.0, pressure=0.0, temperature=300):
        #density in (kg)/m^3 or (mg)/cc
        #pressure in bar
        #temperature in Kelvin
        
        #defaults if not known
        self.DebyeTemp = 420
        
        self.name = name
        self.element = Element(name)
        self.temperature = temperature

        #calculate the number density of the gas in /m^3
        if number_density>0:
            self.number_density = number_density
            
        if mass_density>0:
            self.number_density = mass_density / ( self.molecular_mass() * Constants.atomic_mass )
        
        if pressure>0:
            self.number_density = pressure*1e5 / Constants.boltzmann / temperature
        
        print("Gas fill of "+self.element.name+" at "+str(self.number_density))
        
        
    def molecular_mass(self):
        #returns the mass in atomic units
        return self.element.atomic_mass
    
    def mass_density(self):
        #returns in kg/m^3 = mg/cc
        return self.number_density * self.molecular_mass() * Constants.atomic_mass
    
    def pressure(self):
        #assume ideal gas - returns in bar
        return self.number_density * Constants.boltzmann * self.temperature / 1e5
    
    def conductivity(self, temperature=0):
        #temp in kelvin
        #linear approximation from "Magnetic Fields" Heinz E. Knoepfel page 473 onwards
        
        #search for conductivity if we have it at RTP
        
        #if above debyeTemp
        debyeTemp = self.DebyeTemp
        return debyeTemp*debyeTemp / temperature
    
    
    def phase_state(self):
        return "gas"
    
    
    
    def plasma_beta(self, magnetic_field):
        beta = self.number_density * Constants.boltzmann * self.temperature \
                / magnetic_field/magnetic_field * 2 * Constants.vacuum_permeability
        return beta