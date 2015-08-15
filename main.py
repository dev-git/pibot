# Comments go here

import RPi.GPIO as GPIO
import time
import sys, tty, termios
#import pygame

print 'PiBot initialisation code routine...'

#pygame.init()

# to spam the pygame.KEYDOWN event every 100ms while key being pressed
#pygame.key.set_repeat(100, 100)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

# The getch method can determine which key has been pressed
# by the user on the keyboard by accessing the system files
# It will then return the pressed key as a variable
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

RUNNING = True

try:
   while RUNNING:
    # Keyboard character retrieval method is called and saved
    # into variable
    char = getch()

    # The car will drive forward when the "w" key is pressed
    if(char == "w"):
      print 'forward'
   
    # The car will reverse when the "s" key is pressed
    if(char == "s"):
      print 'back'

# If CTRL+C is pressed the main loop is broken
except KeyboardInterrupt:
   running = False
   print "\nQuitting robot"

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
