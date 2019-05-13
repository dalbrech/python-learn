from time import sleep
import pifacedigitalio

from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt

import numpy as np
time = np.loadtxt('time.txt')

start_time = datetime.now()
mserrlist = [];

#return the elapsed milliseconds since start of program
def millis():
     dt = datetime.now() - start_time
     ms = (dt.days * 24 * 60 *60 +dt.seconds) * 1000 + dt.microseconds/ 1000.0
     return ms

pifacedigitalio.init()
pifacedigital = pifacedigitalio.PiFaceDigital()

statecode = 0

i = 0
while i < len(time):
        
    next_switch_time_s = time[i,0]

    num_repeat = 1
    while( (i+num_repeat < len(time)) and (time[i+num_repeat,0] == time[i,0]) ):
        num_repeat += 1
##    print(num_repeat)
    
    dt = datetime.now() - start_time
    dts = dt.seconds + dt.microseconds/1000000; # current elapsed time
    wait_time = next_switch_time_s - dts
##    print(wait_time)
    
    if(wait_time > 0):
        sleep(wait_time)

    for j in range(num_repeat):
        pin = int(time[i+j,1] - 1)
        state = int(time[i+j,2])
       
        if (state == 1): 
            statecode = (statecode | (1 << pin))
        else:
            statecode = ~(~statecode | (1 << pin))       
        
        # pifacedigital.output_pins[pin].value = state

    pifacedigital.output_port.value = statecode

    mserror = millis() - next_switch_time_s*1000;
    print("%s [%2d] t(s):%0.2f %f (%f ms) :%s" %(datetime.now(), \
            i, next_switch_time_s, millis()/1000, \
            mserror, format(statecode,'08b')))

    mserrlist.append(mserror);

#    print("%s [%d] t(s):%0.2f %f (%f ms) pin:%d state:%d" %(datetime.now(), \
#            i, next_switch_time_s, millis()/1000, \
#            millis() - next_switch_time_s*1000, pin, state))
    
    i += num_repeat


# Summary stats
minerr = np.min(mserrlist[1:])
print("Ignoring first value:")
print("Average error in timing: %f ms +/- %f (SD) ms)" % (np.mean(mserrlist[1:]),np.std(mserrlist[1:])))
print("Ignoring first value and subtracting minimum: %f ms" % minerr)
print("Average error in timing: %f ms +/- %f (SD) ms)" % (np.mean(mserrlist[1:]-minerr),np.std(mserrlist[1:]-minerr)))

plt.subplot(2,1,1)
plt.plot(np.squeeze(mserrlist[1:]-np.mean(mserrlist[1:])))
plt.ylabel("Timing Error [ms]")
plt.xlabel("Switch number")
#plt.show()

# display graph?
pinsUsed = np.unique(time[:,1]) # which pins used

plt.subplot(2,1,2)
for p in pinsUsed:
    ii = np.where(time[:,1] == p)
    plt.step(np.squeeze(time[ii,0]),np.squeeze(time[ii,1]+time[ii,2]*0.8), where='post')
    #plt.plot(time[ii,0],time[ii,1]+time[ii,2]*0.5,'c0o')

#plt.plot(np.squeeze(time[ii,0]),np.squeeze(time[ii,1]+time[ii,2]*0.5),'go-')
plt.xlabel("Time [s]")
plt.ylabel("Pin setting")
plt.show()


      

