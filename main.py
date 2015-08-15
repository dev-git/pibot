# Comments go here

import RPi.GPIO as GPIO
import time

print 'PiBot initialisation code routine...'

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

RUNNING = True

try:
   while RUNNING:
      # Start PWM with the LED off
      pwm.start(0)
      # Randomly change the brightness of the LED
      pwm.ChangeDutyCycle(brightness())
      # Randomly pause on a brightness to simulate flickering
      time.sleep(flicker())

# If CTRL+C is pressed the main loop is broken
except KeyboardInterrupt:
   running = False
   print "\nQuitting Candle Light"

# Actions under 'finally' will always be called, regardless of
# what stopped the program (be it an error or an interrupt)
finally:
   # Stop and cleanup to finish cleanly so the pins
   # are available to be used again
   pwm.stop()
   GPIO.cleanup()
   
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

#GPIO.cleanup()

print 'PiBot initialisation complete.'
