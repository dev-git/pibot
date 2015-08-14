# Comments go here

import RPi.GPIO as GPIO
import time

print 'PiBot initialisation code routine...'

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

GPIO.output(7, True)
time.sleep(1)
GPIO.output(7, False)

GPIO.output(11, True)
time.sleep(1)
GPIO.output(11, False)

GPIO.output(13, True)
time.sleep(1)
GPIO.output(13, False)

GPIO.output(15, True)
time.sleep(1)
GPIO.output(15, False)

GPIO.cleanup()

print 'PiBot initialisation complete.'
