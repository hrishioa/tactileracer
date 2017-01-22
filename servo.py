import wiringpi
import json
import urllib2
import time

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(2, 1)
wiringpi.softPwmCreate(2,0,100)

start_time = time.time()

pins = [2,3,4,17,27,22,11,10,9]

def down(pin):
	wiringpi.softPwmWrite(pins[pin], 23)

def clear():
	for i in xrange(0, 9): control(i, 0)

def up(pin):
	wiringpi.softPwmWrite(pins[pin], 17)

def init():
	for pin in pins:
		wiringpi.pinMode(pin, 1)
		wiringpi.softPwmCreate(pin,0,100)

init()

def pulse(pin, interval):
	if interval == 0:
		control(pin, 0)
	elif (int((time.time() - start)/interval) % 2):
		down(pin)
	else:
		up(pin)

def control(pin, val):
	wiringpi.softPwmWrite(pins[pin], val)

def reset():
	for i in xrange(0,3):
		up(i)
	wiringpi.delay(700)
	for i in xrange(3,6):
		up(i)
	wiringpi.delay(700)
	for i in xrange(6,9):
		up(i)

def redown():
        for i in xrange(0,3):
                down(i)
        wiringpi.delay(700)
        for i in xrange(3,6):
                down(i)
        wiringpi.delay(700)
        for i in xrange(6,9):
                down(i)

def testdown():
        for i in xrange(0,9):
                down(i)
		wiringpi.delay(300)

def testup():
        for i in xrange(0,9):
                up(i)
                wiringpi.delay(300)


def all_move(val):
	for pin in pins:
		wiringpi.softPwmWrite(pin, val)

def move(val):
	wiringpi.softPwmWrite(2,val)

def run(rangelow, rangehigh, inc):
	for i in xrange(rangelow, rangehigh, inc):
		wiringpi.softPwmWrite(2, i)
		wiringpi.delay(100)

def run_pattern(multiplier=1, pattern=None):
	print "Getting pattern..."
	if pattern==None:
		pattern = json.loads(json.loads(urllib2.urlopen('http://dweet.io/get/latest/dweet/for/feelybot').read())['with'][0]['content']['pattern'])
	print "Got Pattern. running..."
	for p in pattern:
		wiringpi.delay(int(p['time']*multiplier))
		print "Cell %d at %d millis." % (p['cell'],p['time'])
		down(p['cell'])

