### Before use install these:
# pip install pifacedigitalio
# pip install PyQt5
# pip install QDarkStyle

from time import sleep
from datetime import datetime
from datetime import timedelta

from PyQt5 import QtGui
import pyqtgraph as pg

import numpy as np
import os

## Check if QDarkStyle is installed
try:
    import qdarkstyle
    darkmode = True
except:
    darkmode = False

## Check if PiFace is installed
try:
    import pifacedigitalio
    piface = True
except:
    print('No PiFace found. Simulation only.')
    piface = False

if piface:
    pifacedigitalio.init()
    pifacedigital = pifacedigitalio.PiFaceDigital()

## Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()
w.setWindowTitle('RasPi Stimulus Controller')

## Check screen size and maximize if RasPi
screen = app.primaryScreen()
size = screen.size()
#print('Size: %d x %d' % (size.width(), size.height()))
if (size.width() < 1024):
    w.showMaximized()

## Create widgets to be placed inside
load = QtGui.QPushButton('Load timing')
enter = QtGui.QPushButton('Enter timing')
save = QtGui.QPushButton('Save timing')
text = QtGui.QLineEdit("[[1,2,10,6,2],[2,2,10,6,4]] # Test pattern")
listw = QtGui.QTextEdit()
graph = pg.PlotWidget(background=1.0)
start = QtGui.QPushButton('Start')
stop = QtGui.QPushButton('STOP!')
if darkmode:
    dark = QtGui.QPushButton('Dark mode')
    dark.setCheckable(True)
    dark.toggle()
    graph.setBackground(0.1)
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)

start.setStyleSheet('QPushButton {color: black; background-color: #80FF80; font-size: 18px; height: 40px}')
stop.setStyleSheet('QPushButton {color: black; background-color: #FF8080; font-size: 18px; height: 40px}')
load.setToolTip('Select a timing file:')
start.setToolTip('Press here to start stimulation')
stop.setToolTip('Press here to abort stimulation')
enter.setToolTip('Press here to select the manual timing from the box below')
save.setToolTip('Press here to save the manual timing (after entering)')
text.setToolTip("Enter manual timing here, in the format: \n"+
                "[[stim#,pulse_width(s),pulse_interval(s),#pulses,start_time(s)]]")
#listw.setFontFamily('Courier New')
listw.setFontPointSize(8)

## Global variables
time = []
abort = False
pos = 0
vert = []
refresh = 0.2 # time marker refresh interval

## return the elapsed milliseconds since start of program (this doesn't seem to work...)
def millis():
     dt = datetime.now() - start_time
     ms = (dt.days * 24 * 60 *60 +dt.seconds) * 1000 + dt.microseconds/ 1000.0
     return ms

## Stimulus state display (show stimuli # active as '~7~5~3~1' instead of '01010101')
def StimState(statecode):
    r = []
    statebin = format(statecode,'08b')
    for j in range(len(statebin)):
        if (statebin[j]=='1'):
            r.append(str(8-j))
        else:
            r.append('~')
    return "".join(r)
    
## Main stimulation function
def stimulate():
    #global abort
    start_time = datetime.now()
    mserrlist = [];
    statecode = 0

    listw.append("Step  ElapsedTime     Error    States")
                 
    i = 0
    while (i < len(time) and abort == False):
        next_switch_time_s = time[i,0]

        num_repeat = 1
        while( (i+num_repeat < len(time)) and (time[i+num_repeat,0] == time[i,0]) ):
            num_repeat += 1

        wait_time = 1.0
        while (wait_time > 0 and abort == False):
            dt = datetime.now() - start_time
            dts = dt.seconds + dt.microseconds/1000000; # current elapsed time
            wait_time = next_switch_time_s - dts
       
            if (wait_time > 0):
                if (wait_time > refresh):
                    sleep(refresh)
                    vert.setValue(dts)
                    graph.setTitle("Stimulus Timing "+str(dt)[:-7])
                    app.processEvents()
                else:
                    sleep(wait_time)

        for j in range(num_repeat):
            pin = int(time[i+j,1] - 1)
            state = int(time[i+j,2])
       
            if (state == 1):
                statecode = (statecode | (1 << pin))
            else:
                statecode = ~(~statecode | (1 << pin))       
        
        if piface:
            pifacedigital.output_port.value = statecode
                
        dt = datetime.now() - start_time; 
        ms = dt.seconds*1000 + dt.microseconds/1000; # current elapsed time (ms)
        mserror = ms - next_switch_time_s*1000;

        #print("%s [%d] t(s):%0.2f" %(datetime.now()-start_time, i, next_switch_time_s))
        #listw.append("%d: %s %0.2f (%f ms)" %(i, datetime.now()-start_time, next_switch_time_s, mserror))
        #listw.append("%d: %s %0.2f (%f ms)" %(i, dt, next_switch_time_s, mserror))
        #listw.append("%3d: %s (%0.2f ms) %s" %(i, dt, mserror, format(statecode,'08b')))
        listw.append("%3d: %s (%0.2f ms) %s" %(i, dt, mserror, StimState(statecode)))
        vert.setValue(next_switch_time_s)
        app.processEvents()

        mserrlist.append(mserror);

        i += num_repeat

    listw.append("Overall timing error: %0.2f +/- %0.2f (sd) ms" %(np.mean(mserrlist), np.std(mserrlist)))
    listw.append("Range: %0.2f - %0.2f ms" %(np.min(mserrlist), np.max(mserrlist)))
##
##        mserror = millis() - next_switch_time_s*1000;
##        #print("%s [%2d] t(s):%0.2f %f (%f ms) :%s" %(datetime.now(), \
##        #    i, next_switch_time_s, millis()/1000, \
##        #    mserror, format(statecode,'08b')))
##
##        mserrlist.append(mserror);
##
##        listw.append("%s [%d] t(s):%0.2f" %(datetime.now()-start_time, i, next_switch_time_s))
##
##        vert.setValue(next_switch_time_s)
##        
##        i += num_repeat




## Pulse pattern definition #####################################

def GenerateMultiPulsePattern(input, sort=1):
    
# timing = GenerateMultiPulsePattern(input, sort)
#
#   input is a n x 5 matrix, each row containing:
#
#       [valve,pwidth,pint,pnum,pstart]
#
#       valve   is an integer stimulus number
#       pwidth  is pulse width in sec.
#       pint    is pulse interval, start to start
#       pnum    is pulse number, or number of cycles
#       pstart  is pulse start, on-time of the first pulse
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

## Log Timing Data to text file
def logTimingData():
    logtext = listw.toPlainText()
    logFileName = 'StimLog_'+datetime.now().strftime("%Y%m%d_%H%M%S.log")
    logfile = open(logFileName,'w')
    logfile.writelines(logtext)
    logfile.close()

## Button Actions

def clickStart():
    global abort
    print('START')
    listw.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": Started")
    
    abort = False
    stimulate()
    listw.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": Ended")
    logTimingData()
start.clicked.connect(clickStart)

def clickStop():
    global abort
    print('STOP')
    listw.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": STOP")
    abort = True
stop.clicked.connect(clickStop)

def updateDisplay():
    graph.clear()
    pinsUsed = np.unique(time[:,1]) # which pins used
    maxtime = np.max(time[:,0])
    #for p in pinsUsed:
    for pn in range(len(pinsUsed)):
        ii = np.where(time[:,1] == pinsUsed[pn])
        #plt.step(np.squeeze(time[ii,0]),np.squeeze(time[ii,1]+time[ii,2]*0.8), where='post')
        x = np.squeeze(time[ii,0])
        #print(np.append(x,x[-1]))
        y = np.squeeze(pn+time[ii,2]*0.8 - 0.4)
        #graph.plot(np.append(x,x[-1]), y, pen=(p,8), stepMode=True)
        graph.plot(np.append(x,maxtime), y, pen=(pinsUsed[pn],8), stepMode=True)
    global vert
    vert = graph.addLine(pos)
    graph.setLabel('left', "Stimulus")
    ax=graph.getAxis('left')    #This is the trick  
    ticks = [list(zip(range(len(pinsUsed)), map(str,map(int,pinsUsed))))]
    ax.setTicks(ticks)
    graph.setLabel('bottom', "Time (s)")
    graph.setTitle("Stimulus Timing")
    graph.setMouseEnabled(y=False)    # mouse scrolls/zooms in x-axis only
    
def openFileNameDialog():
    global time
    qfd = QtGui.QFileDialog()
    options = QtGui.QFileDialog.Options()
    options |= QtGui.QFileDialog.DontUseNativeDialog
    fileName, _ = QtGui.QFileDialog.getOpenFileName(qfd,"Choose a stimulation timing file", "","Text Files (*.txt)",options=options)
    if fileName:
        print(fileName)
        text.setText(fileName)
        time = np.loadtxt(fileName)
        listw.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": Loaded stimulus file: "+fileName)
    else:
        time = np.loadtxt('time.txt')
    #output = '{}'.format(time)
    updateDisplay()
    #print(output)
load.clicked.connect(openFileNameDialog)

def clickEnter():
    import ast
    global time
    print(text.text())
    try:
        pattern = ast.literal_eval(text.text())
        print(pattern)
        time = GenerateMultiPulsePattern(pattern)
        updateDisplay()
    except:
        print("Invalid format.")
enter.clicked.connect(clickEnter)

def clickSave():
    qfd = QtGui.QFileDialog()
    options = QtGui.QFileDialog.Options()
    options |= QtGui.QFileDialog.DontUseNativeDialog
    fileName, _ = QtGui.QFileDialog.getSaveFileName(qfd,"Save stimulation timing file as:","","Text Files (*.txt);;All Files (*)", options=options)
    if fileName:
        print(fileName)
        np.savetxt(fileName, time, fmt="%.2f") # save text timing file
        listw.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+": Saved stimulus file: "+fileName)
save.clicked.connect(clickSave)

def toggleDark():
    #darkmode = not darkmode
    darkmode = dark.isChecked()
    if darkmode:
        graph.setBackground(0.0)
        app.setStyleSheet(dark_stylesheet)
        dark.setText('Dark mode')
    else:
        graph.setBackground(1.0)
        app.setStyleSheet("")
        dark.setText('Light mode')
dark.clicked.connect(toggleDark)
       

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
'''
layout.addWidget(load, 0, 0)   # button goes in upper-left
layout.addWidget(text, 1, 0)   # text edit goes in middle-left
layout.addWidget(listw, 2, 0, 2, 1)  # list widget goes in bottom-left
layout.addWidget(start, 3, 1)  # 
layout.addWidget(stop, 3, 2)   #
layout.addWidget(graph, 0, 1, 3, 2)  # plot goes on right side, spanning 3 rows
'''
layout.addWidget(load, 0, 0)   
layout.addWidget(enter, 0, 1)
layout.addWidget(save, 0, 2) 
layout.addWidget(text, 1, 0, 1, 3)   
#layout.addWidget(listw, 2, 0, 2, 3)  
layout.addWidget(listw, 2, 0, 1, 3)
layout.addWidget(dark, 3, 0)
layout.addWidget(start, 3, 3)  
layout.addWidget(stop, 3, 4)   
layout.addWidget(graph, 0, 3, 3, 2) 


## Display the widget as a new window
w.show()

## Start the Qt event loop
app.exec_()





