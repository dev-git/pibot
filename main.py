# Comments go here

import RPi.GPIO as GPIO
import time
import pygame

print 'PiBot initialisation code routine...'

pygame.init()

# to spam the pygame.KEYDOWN event every 100ms while key being pressed
pygame.key.set_repeat(100, 100)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

RUNNING = True

try:
   while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                print 'go forward'
            if event.key == pygame.K_s:
                print 'go backward'
        if event.type == pygame.KEYUP:
            print 'stop'

# If CTRL+C is pressed the main loop is broken
except KeyboardInterrupt:
   running = False
   print "\nQuitting Candle Light"

# Actions under 'finally' will always be called, regardless of
# what stopped the program (be it an error or an interrupt)
finally:
   # Stop and cleanup to finish cleanly so the pins
   # are available to be used again
   #pwm.stop()
   GPIO.cleanup()
   
#GPIO.output(7, True)
#time.sleep(1)
#GPIO.output(7, False)

#GPIO.output(11, True)
#time.sleep(1)
#GPIO.output(11, False)

#GPIO.output(13, True)
#time.sleep(1)
#GPIO.output(13, False)

#GPIO.output(15, True)
#time.sleep(1)
#GPIO.output(15, False)

#GPIO.cleanup()

print 'PiBot initialisation complete.'
