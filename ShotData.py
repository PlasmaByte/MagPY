#Created by T. Clayson 03/08/17
#class for accessing files on Linna computer in MAGPIE

import os

class ShotData:
    def __init__(self, shotName):
        self.shotName = shotName
        self.shotID = shotName[0:8] #first 8 characters e.g. smmdd_yy
        #get the date
        self.month = int(shotName[1:3])
        self.day = int(shotName[3:5])
        self.year = int(shotName[6:8])
        if self.year>90: #handling Y2K
            self.yearLong = 1900+self.year
        else:
            self.yearLong = 2000+self.year

        self.path = "//LINNA/Users/Magpie/Documents/MAGPIE data/" + str(self.yearLong)

        #find the subfolder based on the month
        monthsShort = ['jan','feb','mar','apr','may','jun','jul','aug', 'sep','oct','nov','dec']
        for subfolder in os.listdir(self.path):
            if monthsShort[self.month-1] in subfolder.lower():
                self.path += "/"+subfolder
        
        #find the actual shot folder
        for subfolder in os.listdir(self.path):
            if self.shotName in subfolder:
                self.path += "/"+subfolder
                print("Folder found: "+self.path)