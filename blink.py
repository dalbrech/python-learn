from time import sleep
import pifacedigitalio

CYCLE = 0.25  # seconds
DELAY = 0.00  # seconds

from datetime import datetime
from datetime import timedelta

start_time = datetime.now()

# returns the elapsed milliseconds since the start of the program
def millis():
   dt = datetime.now() - start_time
   ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
   return ms

def check_sleep(amount):
    start = datetime.now()
    sleep(amount)
    end = datetime.now()
    delta = end - start
    return delta.seconds + delta.microseconds/1000000.

error = sum(abs(check_sleep(DELAY)-DELAY) for i in range(100))*10
print("Average error is %0.2fms" % error)

pifacedigitalio.init()

if __name__ == "__main__":
    pifacedigital = pifacedigitalio.PiFaceDigital()
    while True:
        t1 = datetime.now()
        #print(millis())
        for x in range(0, 8):
             pifacedigital.leds[x].toggle()
             sleep(DELAY)
        #dt = datetime.now() - t1
        dt = datetime.now() - start_time
        dts = dt.seconds + dt.microseconds/1000000;
        st = CYCLE - dts%CYCLE
        #st = CYCLE - dt.microseconds/1000000-0.0003
        if st > 0:
            sleep(st)
        
        print(datetime.now())
