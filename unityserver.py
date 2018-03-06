from servo import *
from time import sleep
from threading import Thread
import subprocess
from bottle import run, post, request, response, get, route


x = 0.0
z = 0.0
hit = False

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

class BackgroundTimer(Thread):   
   def run(self):
      while 1:
        time.sleep(0.1)
        x_pulse = (((abs(x)-X_LOWER)/(X_UPPER-X_LOWER))*(X_MAX_PULSE-X_MIN_PULSE))+(X_MIN_PULSE)
        z_pulse = (((abs(z)-Z_LOWER)/(Z_UPPER-Z_LOWER))*(Z_MAX_PULSE-Z_MIN_PULSE))+(Z_MIN_PULSE)

        print "x pulse is %f and z pulse is %f" % (x_pulse,z_pulse)

        if(x > 0.0): # instruction to go right
            pulse(5, x_pulse)
        if(x < 0.0):
            pulse(3, x_pulse)
        if(z > 0.0): # instruction to go top
            pulse(1, z_pulse)
        if(z < 0.0):
            pulse(7, z_pulse)
            # do something

@post('/')
def unityhandle():
    global x
    global z

    plainx = request.forms.get('X')
    plainz = request.forms.get('Z')
    plainhit = request.forms.get('Hit')

    if(plainx == None):
        print "No unity information being encoded"
        return "<p>No unity information being encoded</p>"

    x = float(plainx)
    z = float(plainz)
    hit = plainhit == "True"

    print("X is %f, Z is %f and Hit is %r" % (x,z,hit))
    return "<p>OK</p>"

timer = BackgroundTimer()
timer.start()

run(host='192.168.43.105', port=9000, debug=True)











