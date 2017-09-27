#Created by T. Clayson 28/07/17
#class for handling and studying shock waves
#Created by T. Clayson 22/09/17
#class for handling a shock and calculating velocities
#able to measure a liner shock from multiframe cameras

import os
import numpy
import matplotlib.pyplot as plt
from scipy import stats
from SourceCode.Multiframe import Multiframe


class Shock:
    def __init__(self, shotID, label=None, fileName=None):
        self.shotID = shotID
        
        if fileName is None:
            self.label = label
        else:
            #determin label from filename
            self.label = fileName.replace("Shock Dynamics","")
            self.label.strip()
        
        self.times = []             #ns
        self.positions = []         #mm
        self.velocity = 0           #km/s
        self.velocity_error = 0     #km/s
        self.start_time = 0         #ns
        self.start_time_error = 0   #ns
        
        self.load_positions(fileName)
        
        
        
    def calculate_velocity(self, current_start=1520, start_position=5.6, silent=False):
        slope, intercept, r_value, p_value, std_err = stats.linregress( self.times,self.positions)
        self.velocity = slope*1000 #defined in km/s
        self.velocity_error = std_err*1000
        self.start_time = (start_position-intercept)/slope - current_start
        
        #determine start time error by calculating min and max time from worst slopes, going through average x and y
        t_mean = numpy.mean(self.times) - current_start
        p_mean = numpy.mean(self.positions)
        start_time_min = t_mean - (p_mean-start_position)/(slope+std_err)
        start_time_max = t_mean - (p_mean-start_position)/(slope-std_err)
        self.start_time_error = abs(start_time_max-start_time_min)/2
        
        if silent is False:
            print("Velocity: "+str(self.velocity)+" +- "+str(self.velocity_error)+" km/s")
            print("Start time: "+str(self.start_time)+" +- "+str(self.start_time_error)+" ns")
            print("== Linear fit data ==")
            print("Slope: "+str(slope))
            print("Intercept: "+str(intercept))
            print("R value: "+str(r_value))
            print("P value: "+str(p_value))
            print("Standard error: "+str(std_err))
            print("\n")



    def __str__(self):  #output from print function
        self.calculate_velocity()
        return ""
        
    
    def clear(self):
        self.times = []
        self.positions = []
        
        
    def append(self, other_shock, multiplier=1):
        self.times = numpy.concatenate( (self.times, other_shock.times), 0)
        new_positions = numpy.array(other_shock.positions)*multiplier
        self.positions = numpy.concatenate( (self.positions, new_positions), 0)
        self.calculate_velocity(silent=True)


    def load_positions(self, fileName=None):
        if self.shotID is None:
            return
        
        path = "Data/"+self.shotID
        
        if fileName is None:
            #find the shock dynamics file
            fileName = None
            for subfile in os.listdir(path):
                if "shock dynamics" in subfile.lower():
                    if self.label is None:
                        fileName = subfile
                    else:
                        if self.label in subfile:
                            fileName = +subfile
                    
            #if no filename is found we will calculate the shock positions
            if fileName is None:
                print("No shock dynamics file found, measuring positions from multiframe images")
                self.measure_from_multiframe()
                return
        
        #load the file
        with open(path+"/"+fileName) as file:
            for l in file:
                line = l.lower()
                if "velocity" in line:
                    if "error" in line:
                        self.velocity_error = float(line.split('=')[1].strip())
                    else:
                        self.velocity = float(line.split('=')[1].strip())
                if "start" in line:
                    if "error" in line:
                        self.start_time_error = float(line.split('=')[1].strip())
                    else:
                        self.start_time = float(line.split('=')[1].strip())
                    
                contents = line.split('\t')
                if len(contents)>1: #find where we actually have a table
                    if "time" not in contents[0]:
                        self.times.append( float(contents[0]) )
                        self.positions.append( float(contents[1]) )
         
        print("Shock positions loaded: "+path+"/"+fileName)
        return self.positions
            
         
            
    def save_positions(self):
        self.calculate_velocity()
        filename = "Data/"+self.shotID+"/Shock Dynamics"
        if self.label is not None:
            filename += " "+self.label
            
        with open(filename, 'w') as file:   #writes file
            file.write( "Shock Velocity (km/s) = "+str(self.velocity)+"\n" )
            file.write( "Shock Velocity error (km/s) = "+str(self.velocity_error)+"\n" )
            file.write( "Shock start time (ns) = "+str(self.start_time)+"\n" )
            file.write( "Shock start time error (ns) = "+str(self.start_time_error)+"\n" )
            
            #output all of the shock positions
            file.write( "\nTime (ns)\tPosition(mm)\n" )
            total_points = min( len(self.times), len(self.positions) )
            for i in range(0, total_points ):
                file.write( str(self.times[i])+"\t"+str(self.positions[i])+"\n" )
    
    
    
    def measure_from_multiframe(self, demo=False, start_frame=1, stop_frame=None, line_thickness=0.1,
                                points_to_check=30, line_start=[5.6,8], line_stop=[14,8], flip=False):
        #line_thickness and slice_height in mm

        #make a multiframe camera object
        multiframe = Multiframe(self.shotID)

        #get lineout from multiframe images averaged over 25 pixels
        self.times = []
        lineOuts = []
        if stop_frame is None:
            stop_frame = multiframe.frames
        for i in range(start_frame, stop_frame+1):
            print("Loading frame "+str(i))
            show_line = False
            if demo is True and i==5:
                show_line = True
            line = multiframe.lineout( i, [line_start[0],line_stop[0],line_start[1],line_stop[1]],
                                      thickness=line_thickness, demo=show_line )
            lineOuts.append( line )
            self.times.append( multiframe.frameTimes[i-1] )
            
        if flip is True:
            for i in range(0, len(lineOuts)):
                lineOuts[i] = numpy.flip(lineOuts[i],0)
            
        #determin if we are plotting horizontal or vertical
        xline = []  #create the xline which follows the major axis
        if abs(line_start[0]-line_stop[0]) > abs(line_start[1]-line_stop[1]):
            xline = numpy.linspace( line_start[0], line_stop[0], len(lineOuts[0]) )
        else:
            xline = numpy.linspace( line_start[1], line_stop[1], len(lineOuts[0]) )
    
#        #determin shock position by finding the first point the line consistently passes the threshold (half the 90th percentile)
#        self.positions = []
#        for line in lineOuts:
#            #threshold ignores first 100 pixels which are not necessarily real
#            threshold = np.percentile( line[100:] , 90 )/2
#            
#            #step through line
#            newShockPosition = 0
#            pixel = len(line)-100 #ignores irst 100 pixels of noise
#            while newShockPosition==0 and pixel>0:
#                pixel -= 1
#                if all(i >= threshold for i in line[pixel-5:pixel+1]) is True:
#                    newShockPosition = pixel/multiframe.scale + multiframe.offset[0]
#            
#            self.positions.append(newShockPosition)
            
#        #determin shock position by finding a maximum point surrounded by other points >mean
#        self.positions = []
#        ignore_points = 100  #ignores first 100 pixels ~ noise
#        for line in lineOuts:
#            #threshold 
#            mean = numpy.mean( line[ignore_points:] )
#            #step through maximums and check points to the left are also above mean
#            max_positions = numpy.argsort( -line[ignore_points:] )
#            for max_point in max_positions:
#                points_to_check = 10
#                pixel = max_point+100
#                if all(i > mean for i in line[pixel-points_to_check:pixel]) is True:
#                    newShockPosition = pixel/multiframe.scale + multiframe.offset[0]
#                    self.positions.append(newShockPosition)
#                    break
            
        #determin shock position by finding the maximum gradient
        #gradient = averages either side of point - removes nosie ect
        self.positions = []
        for line in lineOuts:
            best_pixel, best_gradient = 0,0
            for pixel in range(points_to_check, len(line)-points_to_check ):
               gradient = numpy.mean( line[pixel-points_to_check:pixel] ) - numpy.mean( line[pixel:pixel+points_to_check] )
               if gradient>best_gradient:
                   best_gradient = gradient
                   best_pixel = pixel

            newShockPosition = xline[best_pixel]
            self.positions.append(newShockPosition)


        if demo is True:
            #plot lineouts with shock positions
            fig, axd = plt.subplots(4,3)
            for i in range(0, stop_frame-start_frame+1):
                ax_sub = axd[ int(i/3), i%3 ]
                ax_sub.plot( xline, lineOuts[i])
                ylims = ax_sub.get_ylim()
                ax_sub.plot( [ self.positions[i], self.positions[i]], ylims, "--")
                ax_sub.set_xlabel("")
                ax_sub.set_ylabel("")
        
            #Thesis plot
            fig, axT = plt.subplots()
            frames = [2,6,10]
            colors = ['r','b','g']
            for i in range(0, len(frames)):
                axT.plot(xline, lineOuts[i], colors[i])
            ylims = ax_sub.get_ylim()
            for i in range(0, len(frames)): #plot shock positions
                axT.plot( [self.positions[i],self.positions[i]] , ylims, colors[i]+'--')
            axT.set_xlabel("Position [mm]")
            axT.set_ylabel("Intensity [AU]")

            plt.grid(True)
            
        #show that the shock front position selection isn't stupid
        if demo is True:
            measure_points = []
            ptcline = range(1,100)
            for ptc in ptcline:
                line = lineOuts[5]
                best_pixel, best_gradient = 0,0
                for pixel in range(ptc, len(line)-ptc ):
                    gradient = numpy.mean( line[pixel-ptc:pixel] ) - numpy.mean( line[pixel:pixel+ptc] )
                    if gradient>best_gradient:
                        best_gradient = gradient
                        best_pixel = pixel

                newShockPosition = xline[best_pixel]
                measure_points.append(newShockPosition)
            fig, axTest = plt.subplots()
            axTest.plot(ptcline, measure_points)
            axTest.set_xlabel("Points averaged over")
            axTest.set_ylabel("Shock position [mm]")
            plt.grid(True)
            
        self.calculate_velocity()
        self.plot()
        
        
    def remove_frames(self, ignore_frames=[]):
        #removes frames we should ignore
        removed_times = []
        removed_positions = []
        ignore_frames.sort(reverse=True)    #sorts so indecies don't get confused
        for f in ignore_frames:
            frame = f-1
            removed_times.append( self.times[frame] )
            removed_positions.append( self.positions[frame] )
            del self.times[frame]
            del self.positions[frame]

        return [removed_times,removed_positions]
            
    
    
    def plot(self, ax=None, color="b", trendline=True, xerr=2, yerr=0.25, 
             current_start=1520, multiplier=1, solid_line=False):
        #standard errors for T. Claysons setup position=250um, time=2ns
        if ax is None:
            fig, ax=plt.subplots()
            
        plot_times = numpy.array(self.times)-current_start
        plot_positions = numpy.array(self.positions)*multiplier
        if solid_line is True:
            ax.plot(plot_times, plot_positions, color)  # plot lines
        ax.errorbar(plot_times, plot_positions, fmt=color+".", xerr=xerr, yerr=yerr, ecolor=color)   # plots errorbars
        ax.plot(plot_times, plot_positions, color+'o')  # plots points
        ax.set_xlabel("Time [ns]")
        ax.set_ylabel("Position [mm]")
        ax.set_title("Shock position over time for "+self.shotID)
        plt.grid(True)
        
        #plot linear trendline
        if trendline is True:
            slope, intercept, r_value, p_value, std_err = stats.linregress( plot_times,self.positions)
            xValues = numpy.array([ plot_times[0], plot_times[-1] ])
            yValues = xValues*slope +intercept
            yValues = numpy.array(yValues)*multiplier
            ax.plot( xValues,yValues, color+'--' )
            
        
        return ax