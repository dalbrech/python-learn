from time import sleep
import pifacedigitalio

from datetime import datetime
from datetime import timedelta

import numpy as np
time = np.loadtxt('time.txt')
#CYCLE = time[:, 0]
##DELAY = 0.000
##on_off = time[:, 2]
##print(on_off)

##j = 0
##while j<time.size:
##    k=j+1
##    CYCLE = time[k,0]-time[j,0]
##    j = j+1
##    print(CYCLE)

start_time = datetime.now()

#return the elapsed milliseconds since start of program
def millis():
     dt = datetime.now() - start_time
     ms = (dt.days * 24 * 60 *60 +dt.seconds) * 1000 + dt.microseconds/ 1000.0
     return ms

##def check_sleep(amount):
##     start = datetime.now()
##     sleep(amount)
##     end = datetime.now()
##     delta = end - start
##     return delta.seconds + delta.microseconds/1000000.
##
##error = sum(abs(check_sleep(DELAY)-DELAY) for i in range(100))*10
##print("Average error is %0.2fms" %error)

pifacedigitalio.init()
pifacedigital = pifacedigitalio.PiFaceDigital()

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
    
        pifacedigital.output_pins[pin].value = state


        print("%s [%d] t(s):%0.2f %f (%f ms) pin:%d state:%d" %(datetime.now(), \
            i, next_switch_time_s, millis()/1000, \
            millis() - next_switch_time_s*1000, pin, state))
    
    i += num_repeat


##    if(time[i,2]==1):
##        pifacedigital.output_pins[7].value = 1
##        #print('on')
##        dt = datetime.now() - start_time
##        dts = dt.seconds + dt.microseconds/1000000;
##        st = CYCLE - dts%CYCLE
##        print(datetime.now())
##        i = i+1
##    elif(time[i,2]==0):
##        pifacedigital.output_pins[7].value = 0
##        #print('off')
##        dt = datetime.now() - start_time
##        dts = dt.seconds + dt.microseconds/1000000;
##        st = CYCLE - dts%CYCLE
##        print(datetime.now())
##        i=i+1
