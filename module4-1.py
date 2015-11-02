# Comments go here

import RPi.GPIO as GPIO
import time
import sys, tty, termios

print 'Hit X to exit the program'

GPIO.setmode(GPIO.BOARD)

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
    #char = getch()

    #if(char == "x"):
    #    RUNNING = False
        #print "\nPiBot is going offline."
    #    break
    
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

    # The keyboard character variable will be set to blank, ready
    # to save the next key that is pressed
    #char = ""      
      
# If CTRL+C is pressed the main loop is broken
except KeyboardInterrupt:
   RUNNING = False
   print "\nQuitting robot"

# Actions under 'finally' will always be called, regardless of
# what stopped the program (be it an error or an interrupt)
finally:
   # Stop and cleanup to finish cleanly so the pins
   # are available to be used again
   GPIO.cleanup()
   
print "\nPiBot is going offline..."
#GPIO.cleanup()
