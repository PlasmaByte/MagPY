#Created by T. Clayson 28/09/17
#class for storing constants - everything is in standard units

class Constants:
    boltzmann =  1.38064852e-23             #https://en.wikipedia.org/wiki/Boltzmann_constant
    atomic_mass = 1.660539040e-27           #Unified atomic mass unit = https://en.wikipedia.org/wiki/Unified_atomic_mass_unit
    vacuum_permittivity = 8.854187817e-12   #https://en.wikipedia.org/wiki/Vacuum_permittivity
    vacuum_permeability = 1.2566370614e-6   #https://en.wikipedia.org/wiki/Vacuum_permeability
    electron_charge = 1.6021766208e-19      #https://en.wikipedia.org/wiki/Elementary_charge
    
    @staticmethod
    def kelvin_to_eV(temperature_kelvin):
        return temperature_kelvin * Constants.boltzmann / Constants.electron_charge
    
    @staticmethod
    def eV_to_kelvin(temperature_eV):
        return temperature_eV / Constants.boltzmann * Constants.electron_charge