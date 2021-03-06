# Traffic light prog
import RPi.GPIO as GPIO
import time

print 'PiBot initialisation code routine...'

# What Raspberry Pi revision are we running?  
GPIO.RPI_REVISION     #  0 = Compute Module, 1 = Rev 1, 2 = Rev 2, 3 = Model B+  
  
# What version of RPi.GPIO are we running?  
GPIO.VERSION   

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

print 'Turn on red light\n'
GPIO.output(11, True)
time.sleep(2)
GPIO.output(11, False)

print 'Turn on orange light\n'    
GPIO.output(13, True)
time.sleep(2)
GPIO.output(13, False)

print 'Turn on green light\n' 

GPIO.output(15, True)
time.sleep(2)
GPIO.output(15, False)

GPIO.cleanup()

print 'Program complete.'
