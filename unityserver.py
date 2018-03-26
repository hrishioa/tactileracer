from servo import *
from time import sleep
from threading import Thread
import subprocess
from bottle import run, post, request, response, get, route
import time


x = 0.0
z = 0.0
hit = False
linearup = False

X_UPPER = 3.0
X_LOWER = 0.0
Z_UPPER = 3.0
Z_LOWER = 0.0

MAX_PULSE = 0.1
MIN_PULSE = 0.5
X_MAX_PULSE = MAX_PULSE
X_MIN_PULSE = MIN_PULSE
Z_MAX_PULSE = MAX_PULSE
Z_MIN_PULSE = MIN_PULSE

HITPULSECYCLES = 10
HITPULSE = 0.1

clear()

hittime = 0.0
hitduration = 1.0
hitcountdown = 0

class BackgroundTimer(Thread):   
   def run(self):
      while 1:
        time.sleep(0.1)

        if linearup is True:
            x_pulse = (((abs(x)-X_LOWER)/(X_UPPER-X_LOWER))*(X_MAX_PULSE-X_MIN_PULSE))+(X_MIN_PULSE)
            z_pulse = (((abs(z)-Z_LOWER)/(Z_UPPER-Z_LOWER))*(Z_MAX_PULSE-Z_MIN_PULSE))+(Z_MIN_PULSE)
        else:
            x_pulse = ((((X_UPPER-(abs(x)-X_LOWER))-X_LOWER)/(X_UPPER-X_LOWER))*(X_MAX_PULSE-X_MIN_PULSE))+(X_MIN_PULSE)
            z_pulse = ((((Z_UPPER-(abs(z)-Z_LOWER))-Z_LOWER)/(Z_UPPER-Z_LOWER))*(Z_MAX_PULSE-Z_MIN_PULSE))+(Z_MIN_PULSE)

        print "x pulse is %f and z pulse is %f" % (x_pulse,z_pulse)

        if(x > 0.0): # instruction to go right
            pulse(2, x_pulse)
        if(x < 0.0):
            pulse(3, x_pulse)
        if(z > 0.0): # instruction to go top
            pulse(1, z_pulse)
        if(z < 0.0):
            pulse(7, z_pulse)

        print "Hittime is %f, current is %f, hitduration is %f" % (hittime, time.time(), hitduration)
        if (time.time()-hittime) < hitduration:
            print "Hitcountdown activated"
            pulse(4, HITPULSE)


@post('/')
def unityhandle():
    global x
    global z
    global hit
    global linearup
    global hittime

    plainx = request.forms.get('X')
    plainz = request.forms.get('Z')
    plainhit = request.forms.get('Hit')
    plainlinearup = request.forms.get('LinearUp')

    if(plainx == None):
        print "No unity information being encoded"
        return "<p>No unity information being encoded</p>"

    linearup = plainlinearup == "True"
    x = float(plainx)
    z = float(plainz)
    hit = plainhit == "True"

    if hit is True:
        print "Hit"
        # hitcountdown = HITPULSECYCLES
        hittime = time.time()

    print("X is %f, Z is %f, LinearUp is %r and Hit is %r" % (x,z,linearup,hit))
    return "<p>OK</p>" 

timer = BackgroundTimer()
timer.start()

run(host='192.168.43.105', port=9000, debug=True)











