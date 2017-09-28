import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import scipy.integrate
import math
from SourceCode.Material import Material

class Liner:
    def __init__(self, material="steel", length=20e-3, diameter=11e-3, thickness=0.1e-3, cathode=5e-3):
        self.material = Material(material)
        self.length = length
        self.diameter = diameter
        self.thickness = thickness
        self.cathode = cathode
        
        #calculate resistance
        resistivity = 1/self.material.Conductivity()
        self.resistance = resistivity * length / 2 / math.pi / (diameter/2) / (thickness)
        
        #calculate inductance
        fieldArea = length*(diameter-cathode)/2
        fieldPath = math.pi*(diameter+cathode)
        self.inductance = 4e-7*math.pi * fieldArea / fieldPath
        
    def Impedance(self, frequency):
        return self.resistance + 2*math.pi*frequency * self.inductance