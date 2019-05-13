def GenerateMultiPulsePattern(input, sort=1):
    
# timing = GenerateMultiPulsePattern(input, sort)
#
#   input is a n x 5 matrix, each row containing:
#
#       [valve,pwidth,pint,pnum,pstart]
#
#       valve   is an integer stimulus number
#       pwidth  is pulse width in sec.
#       pint    is pulse interval, start to start
#       pnum    is pulse number, or number of cycles
#       pstart  is pulse start, on-time of the first pulse
#
#   example: input = [[1,5,60,10,5],[2,10,60,10,10]]
#
#   sort = 1 sorts the output matrix by ascending time
#

    import numpy as np

    numpatterns = len(input)            # how many patterns (input rows)
    alltiming = np.empty((0,3), int)    # initialize timing array

    for p in range(0,numpatterns):      # loop through each row

        [valve,pwidth,pint,pnum,pstart] = input[p]  # populate vars for each row

        time = pstart
        timing = np.zeros((2*pnum,3))   # on and off for each pulse
        for i in range(0, 2*pnum):
            if (i % 2) == 0:
                timing[i] = [time, valve, 1];
            else:
                timing[i] = [time + pwidth, valve, 0];
                time = time + pint
        if (pstart > 0):    # set valve to 0 at time 0 if first pulse is after t=0
            timing = np.insert(timing, 0, [0, valve, 0], axis=0)
            
        #print(timing)
        alltiming = np.append(alltiming, timing, axis=0)    # add the next pattern to the list

    #sort the final matrix by time?
    if sort:
        sortidx = np.argsort(alltiming, axis=0) # get sort index along columns
        alltiming = alltiming[sortidx[:,0]]     # rearrange accroding to first column (time)
        
    return alltiming


'''
valve = input("Valve number: ")
valve = int(valve)

pwidth = input("Pulse width in seconds: ")
pwidth = int(pwidth)

pint = input("Pulse interval, start to start: ")
pint = int(pint)

pnum = input("Pulse number (number of cycles): ")
pnum = int(pnum)

pstart = input("On-Time of the first pulse: ")
pstart = int(pstart)
'''

import numpy as np

#input = [[1,1,6,10,5],[2,1.5,6,10,6],[8,0.5,2,30,1.5]]
#input = [[1,0.1,0.6,10,0.5],[2,0.15,0.6,10,0.6],[8,0.05,0.2,30,0.15]]
#input = [[1,0.1,1,20,0.5],[2,0.2,2,10,.2],[8,0.3,1.5,15,0]]
#input = [[1,0.01,0.1,20,0.05],[2,0.02,0.2,10,.02],[8,0.03,.15,15,0]]

totalTime = 20.
rate = 0.2
input = [[8,    rate*1, 5*rate,     int(totalTime/rate/5),  rate*1],    
         [7,    rate*2, 10*rate,    int(totalTime/rate/10), rate*2],      
         [6,    rate*3, 15*rate,    int(totalTime/rate/15), rate*3],      
         [5,    rate*4, 20*rate,    int(totalTime/rate/20), rate*4],      
         [4,    rate*5, 25*rate,    int(totalTime/rate/25), rate*5]]

timing = GenerateMultiPulsePattern(input)

np.savetxt('time.txt', timing , fmt="%.2f") 
