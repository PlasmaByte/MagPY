#Created by T. Clayson 27/09/17
#class for handling standard gas calculations

from SourceCode.Element import Element


class Gas:
            
    def __init__(self, gas="He", number_density=0.0, mass_density=0.0, pressure=0.0, temperature=300):
        #density in (kg)/m^3 or (mg)/cc
        #pressure in bar
        #temperature in Kelvin
        
        self.element = Element(gas)
        self.temperature = temperature

        #calculate the number density of the gas in /m^3
        if number_density>0:
            self.number_density = number_density
            
        if mass_density>0:
            self.number_density = mass_density / ( self.molecular_mass() * 1.660539040e-27 )
        
        if pressure>0:
            self.number_density = pressure*1e5 / 1.38064852e-23 / temperature
        
        print("Gas fill of "+self.element.name+" at "+str(self.number_density))
        
        
    def molecular_mass(self):
        #returns the mass in atomic units
        return self.element.atomic_mass
    
    
    
    def mass_density(self):
        #returns in kg/m^3 = mg/cc
        return self.number_density * self.molecular_mass() * 1.660539040e-27
    
    
    
    def pressure(self):
        #assume ideal gas - returns in bar
        return self.number_density * 1.38064852e-23 * self.temperature / 1e5