import RPi.GPIO as GPIO
import time
#import sys, tty, termios

print 'Programming the bot...'

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

def forward(interval):
      print 'forward'
      GPIO.output(11, True)
      GPIO.output(13, True)
      time.sleep(1)
      GPIO.output(11, False)
      GPIO.output(13, False)
   
def back(interval):
      print 'back'
      GPIO.output(7, True)
      GPIO.output(15, True)
      time.sleep(interval)
      GPIO.output(7, False)
      GPIO.output(15, False)

def left(interval):
      print 'left'
      GPIO.output(13, True)
      time.sleep(interval)
      GPIO.output(13, False)
      
def right(interval):
      print 'right'
      GPIO.output(11, True)
      time.sleep(interval)
      GPIO.output(11, False)
      
forward(1)
right(3)
left(2)
back(5)
forward(2)

GPIO.cleanup()
   
print "\nPiBot is going offline..."
      
      
