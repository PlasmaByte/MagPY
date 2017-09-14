#Created by T. Clayson 31/08/17
#class for performing abel transformations

import numpy as np
import matplotlib.pyplot as plt



def AbelTransform1D(inData, origin=0):
    #uses the shell method (ask Thomas or Francisco)
    
    xsize = len(inData)
    output = np.zeros(xsize) # array to store the output
    output[0] = 0 # boundary
    
    for i in range( 1 ,  xsize-origin ):
        icord = xsize-i
        output[icord] = 0
        yi = float(xsize-origin - i)
        for j in range( 1 , i ):
            jcord = xsize-j
            yj = float(xsize-origin - j)
            Xij = np.sqrt( (yj+1)*(yj+1) - yi*yi ) - np.sqrt( yj*yj - yi*yi )
            output[icord] += float(inData[jcord]) * Xij

        output[icord] = 2 * output[icord] / xsize

    #for x in range( 0 ,  xsize-origin ):
    #    xcord = x+origin
    #    output[xcord] = 0
    #    yi = float(xsize-origin - i)
    #    for r in range( x+1 , xsize-origin-1 ):
    #        yj = float(xsize-origin - j)
    #        rcord = origin+r
    #        Xij = np.sqrt( (yj+1)*(yj+1) - yi*yi ) - np.sqrt( yj*yj - yi*yi )
    #        output[xcord] += float(inData[rcord]) * Xij
            
            #output[xcord] += float(inData[rcord]) * rf / np.sqrt( rf*rf-xf*xf )
            
    #   output[xcord] = 2 * output[xcord] / xsize
                   
    return output



def AbelInverse1D(inData, origin=0):
    #uses the shell method (ask Thomas or Francisco)
    
    xsize = len(inData)
    output = np.zeros(xsize) # array to store the output
    output[0] = 0 # boundary
        
    for i in range(2 , xsize-origin):
        icord = xsize-i
        yi = float(xsize-origin - i)
        Xii = np.sqrt( (yi+1)*(yi+1) - yi*yi )
        output[icord] = inData[icord]/2
            
        for j in range(1 , i):
            jcord = xsize-j
            yj = float(xsize-origin - j)
            Xij = np.sqrt( (yj+1)*(yj+1) - yi*yi ) - np.sqrt( yj*yj - yi*yi )
            output[icord] = output[icord] - output[jcord] * Xij
            
        output[icord] = output[icord] / Xii
    
    output = output*xsize
    
    #remove negatives
    
    return output
    
    
    
def AbelTest(): #performs a test to proove that the above code actually works - transforms a and then inverse transforms functions
    
    #circle function
    circle = np.zeros(2000)
    for i in range(0,1000):
        circle[i] = np.sqrt( 1000*1000-i*i )
    inverse = AbelInverse1D(circle)
    fig, ax0 = plt.subplots()
    ax0.plot( circle , label='Original')
    ax0.plot( inverse , label='InverseVersion' )
    ax0.legend(loc='upper right')
    
    #step function
    step = np.zeros(2000)
    step[0:1000] = 1000
    abel = AbelTransform1D(step)
    inverse = AbelInverse1D(abel)
    fig, ax1 = plt.subplots()
    ax1.plot( step , label='Original')
    ax1.plot( abel , label='Abel' )
    ax1.plot( inverse , label='Inverse' )
    ax1.legend(loc='upper right')
    
    #thin shell
    shell = np.zeros(2000)
    shell[900:1000] = 1
    abel2 = AbelTransform1D(shell)
    inverse2 = AbelInverse1D(abel2)
    fig, ax2 = plt.subplots()
    ax2.plot( shell , label='Original')
    ax2.plot( abel2 , label='Abel' )
    ax2.plot( inverse2 , label='Inverse' )
    ax2.legend(loc='upper right')