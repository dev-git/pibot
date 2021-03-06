#!/usr/bin/env python
# coding: Latin-1

# Creates a web-page interface for 4Borg

# Import library functions we need
import RPi.GPIO as GPIO
import time
import sys
import threading
import SocketServer
#import picamera
#import picamera.array
import cv2
import datetime

#GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)

# Settings for the web-page
webPort = 80                            # Port number for the web-page, 80 is what web-pages normally use
imageWidth = 240                        # Width of the captured image in pixels
imageHeight = 180                       # Height of the captured image in pixels
frameRate = 10                          # Number of images to capture per second
displayRate = 2                         # Number of images to request per second
photoDirectory = '/home/pi'             # Directory to save photos to

# Global values
global PBR
global lastFrame
global lockFrame
global camera
global processor
global running
global watchdog
running = True


# Power settings
voltageIn = 6.0                         # Total battery voltage to the PicoBorg Reverse (change to 9V if using a non-rechargeable battery)
voltageOut = 6.0                        # Maximum motor voltage

# Setup the power limits
if voltageOut > voltageIn:
    maxPower = 1.0
else:
    maxPower = voltageOut / float(voltageIn)

# Timeout thread
class Watchdog(threading.Thread):
    def __init__(self):
        super(Watchdog, self).__init__()
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.timestamp = time.time()

    def run(self):
        timedOut = True
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for a network event to be flagged for up to one second
            if timedOut:
                if self.event.wait(1):
                    # Connection
                    print 'Reconnected...'
                    timedOut = False
                    self.event.clear()
            else:
                if self.event.wait(1):
                    self.event.clear()
                else:
                    # Timed out
                    print 'Timed out...'
                    timedOut = True
                    # PBR.MotorsOff()

# Image stream processing thread
class StreamProcessor(threading.Thread):
    def __init__(self):
        super(StreamProcessor, self).__init__()
        #self.stream = picamera.array.PiRGBArray(camera)
        self.event = threading.Event()
        self.terminated = False
        self.start()
        self.begin = 0

    def run(self):
        global lastFrame
        global lockFrame
        # This method runs in a separate thread
        while not self.terminated:
            # Wait for an image to be written to the stream
            if self.event.wait(1):
                try:
                    # Read the image and save globally
                    self.stream.seek(0)
                    flippedArray = cv2.flip(self.stream.array, -1) # Flips X and Y
                    retval, thisFrame = cv2.imencode('.jpg', flippedArray)
                    del flippedArray
                    lockFrame.acquire()
                    lastFrame = thisFrame
                    lockFrame.release()
                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()

# Image capture thread
class ImageCapture(threading.Thread):
    def __init__(self):
        super(ImageCapture, self).__init__()
        self.start()

    def run(self):
        global camera
        global processor
        print 'Start the stream using the video port'
        camera.capture_sequence(self.TriggerStream(), format='bgr', use_video_port=True)
        print 'Terminating camera processing...'
        processor.terminated = True
        processor.join()
        print 'Processing terminated.'

    # Stream delegation loop
    def TriggerStream(self):
        global running
        while running:
            if processor.event.is_set():
                time.sleep(0.01)
            else:
                yield processor.stream
                processor.event.set()

# Class used to implement the web server
class WebServer(SocketServer.BaseRequestHandler):
    def handle(self):
        global PBR
        global lastFrame
        global watchdog
        # Get the HTTP request data
        reqData = self.request.recv(1024).strip()
        reqData = reqData.split('\n')
        # Get the URL requested
        getPath = ''
        for line in reqData:
            if line.startswith('GET'):
                parts = line.split(' ')
                getPath = parts[1]
                break
        watchdog.event.set()
        if getPath.startswith('/cam.jpg'):
            # Camera snapshot
            lockFrame.acquire()
            sendFrame = lastFrame
            lockFrame.release()
            if sendFrame != None:
                self.send(sendFrame.tostring())
        elif getPath.startswith('/off'):
            # Turn the drives off
            httpText = '<html><body><center>'
            httpText += 'Speeds: 0 %, 0 %'
            httpText += '</center></body></html>'
            self.send(httpText)
            # PBR.MotorsOff()
        elif getPath.startswith('/set/'):
            # Motor power setting: /set/driveLeft/driveRight
            parts = getPath.split('/')
            # Get the power levels
            if len(parts) >= 4:
                try:
                    #print 'Parts...'
                    #print parts[2]
                    #print parts[3]
                    driveLeft = float(parts[2])
                    driveRight = float(parts[3])
                except:
                    # Bad values
                    driveRight = 0.0
                    driveLeft = 0.0
            else:
                # Bad request
                driveRight = 0.0
                driveLeft = 0.0
            # Ensure settings are within limits
            if driveRight < -1:
                driveRight = -1
            elif driveRight > 1:
                driveRight = 1
                
            if driveLeft < -1:
                driveLeft = -1
            elif driveLeft > 1:
                driveLeft = 1
            # Report the current settings
            percentLeft = driveLeft * 100.0;
            percentRight = driveRight * 100.0;
            httpText = '<html><body><center>'
            httpText += 'Speeds: %.0f %%, %.0f %%' % (percentLeft, percentRight)
            httpText += '</center></body></html>'
            self.send(httpText)
            # Set the outputs
            #driveLeft *= maxPower
            #driveRight *= maxPower
            # PBR.SetMotor1(-driveLeft)
            # PBR.SetMotor2(driveRight)
            
            if (driveLeft == 1 and driveRight == 1):
                # forward
                print 'Going forward...'
                GPIO.output(11, True)
                GPIO.output(13, True)
                time.sleep(1)
                GPIO.output(11, False)
                GPIO.output(13, False)
            elif (driveLeft == 1 and driveRight == -1):     
                # Left
                print 'Turning left...'
                GPIO.output(13, True)
                time.sleep(0.1)
                GPIO.output(13, False)
            elif (driveLeft == -1 and driveRight == 1): 
                print 'Turning right...'
                GPIO.output(11, True)
                time.sleep(0.1)
                GPIO.output(11, False)                
            elif (driveLeft == -1 and driveRight == -1): 
                # Reverse
                print 'Reversing...'
                GPIO.output(7, True)
                GPIO.output(15, True)
                time.sleep(1)
                GPIO.output(7, False)
                GPIO.output(15, False)
            else:
                print 'Oops'

        elif getPath.startswith('/photo'):
            # Save camera photo
            lockFrame.acquire()
            captureFrame = lastFrame
            lockFrame.release()
            httpText = '<html><body><center>'
            if captureFrame != None:
                photoName = '%s/Photo %s.jpg' % (photoDirectory, datetime.datetime.utcnow())
                try:
                    photoFile = open(photoName, 'wb')
                    photoFile.write(captureFrame)
                    photoFile.close()
                    httpText += 'Photo saved to %s' % (photoName)
                except:
                    httpText += 'Failed to take photo!'
            else:
                httpText += 'Failed to take photo!'
            httpText += '</center></body></html>'
            self.send(httpText)
        elif getPath == '/':
            # Main page, click buttons to move and to stop
            httpText = '<html>\n'
            httpText += '<head>\n'
            httpText += '<script language="JavaScript"><!--\n'
            httpText += 'function Drive(left, right) {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' var slider = document.getElementById("speed");\n'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;\n'
            httpText += '}\n'
            httpText += 'function Off() {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' iframe.src = "/off";\n'
            httpText += '}\n'
            httpText += 'function Photo() {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' iframe.src = "/photo";\n'
            httpText += '}\n'
            httpText += '//--></script>\n'
            httpText += '</head>\n'
            httpText += '<body>\n'
            #httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>\n'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>\n'
            httpText += '<center>\n'
            httpText += '<button onclick="Drive(-1,1)" style="width:200px;height:100px;"><b>Spin Left</b></button>\n'
            httpText += '<button onclick="Drive(1,1)" style="width:200px;height:100px;"><b>Forward</b></button>\n'
            httpText += '<button onclick="Drive(1,-1)" style="width:200px;height:100px;"><b>Spin Right</b></button>\n'
            httpText += '<br /><br />\n'
            #httpText += '<button onclick="Drive(0,1)" style="width:200px;height:100px;"><b>Turn Left</b></button>\n'
            httpText += '<button onclick="Drive(-1,-1)" style="width:200px;height:100px;"><b>Reverse</b></button>\n'
            #httpText += '<button onclick="Drive(1,0)" style="width:200px;height:100px;"><b>Turn Right</b></button>\n'
            #httpText += '<br /><br />\n'
            #httpText += '<button onclick="Off()" style="width:200px;height:100px;"><b>Stop</b></button>\n'
            httpText += '<br /><br />\n'
            #httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>\n'
            httpText += '<br /><br />\n'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />\n'
            httpText += '</center>\n'
            httpText += '</body>\n'
            httpText += '</html>\n'
            self.send(httpText)
        elif getPath == '/hold':
            # Alternate page, hold buttons to move (does not work with all devices)
            httpText = '<html>\n'
            httpText += '<head>\n'
            httpText += '<script language="JavaScript"><!--\n'
            httpText += 'function Drive(left, right) {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' var slider = document.getElementById("speed");\n'
            httpText += ' left *= speed.value / 100.0;'
            httpText += ' right *= speed.value / 100.0;'
            httpText += ' iframe.src = "/set/" + left + "/" + right;\n'
            httpText += '}\n'
            httpText += 'function Off() {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' iframe.src = "/off";\n'
            httpText += '}\n'
            httpText += 'function Photo() {\n'
            httpText += ' var iframe = document.getElementById("setDrive");\n'
            httpText += ' iframe.src = "/photo";\n'
            httpText += '}\n'
            httpText += '//--></script>\n'
            httpText += '</head>\n'
            httpText += '<body>\n'
            httpText += '<iframe src="/stream" width="100%" height="500" frameborder="0"></iframe>\n'
            httpText += '<iframe id="setDrive" src="/off" width="100%" height="50" frameborder="0"></iframe>\n'
            httpText += '<center>\n'
            httpText += '<button onmousedown="Drive(-1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Left</b></button>\n'
            httpText += '<button onmousedown="Drive(1,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Forward</b></button>\n'
            httpText += '<button onmousedown="Drive(1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Spin Right</b></button>\n'
            httpText += '<br /><br />\n'
            httpText += '<button onmousedown="Drive(0,1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Left</b></button>\n'
            httpText += '<button onmousedown="Drive(-1,-1)" onmouseup="Off()" style="width:200px;height:100px;"><b>Reverse</b></button>\n'
            httpText += '<button onmousedown="Drive(1,0)" onmouseup="Off()" style="width:200px;height:100px;"><b>Turn Right</b></button>\n'
            httpText += '<br /><br />\n'
            httpText += '<button onclick="Photo()" style="width:200px;height:100px;"><b>Save Photo</b></button>\n'
            httpText += '<br /><br />\n'
            httpText += '<input id="speed" type="range" min="0" max="100" value="100" style="width:600px" />\n'
            httpText += '</center>\n'
            httpText += '</body>\n'
            httpText += '</html>\n'
            self.send(httpText)
        else:
            # Unexpected page
            self.send('Path : "%s"' % (getPath))

    def send(self, content):
        self.request.sendall('HTTP/1.0 200 OK\n\n%s' % (content))


# Create the image buffer frame
#lastFrame = None
#lockFrame = threading.Lock()

# Startup sequence
#print 'Setup camera'
#camera = picamera.PiCamera()
#camera.resolution = (imageWidth, imageHeight)
#camera.framerate = frameRate

print 'Setup the stream processing thread'
processor = StreamProcessor()

print 'Wait ...'
time.sleep(2)
#captureThread = ImageCapture()

print 'Setup the watchdog'
watchdog = Watchdog()

# Run the web server until we are told to close
httpServer = SocketServer.TCPServer(("0.0.0.0", webPort), WebServer)
try:
    print 'Press CTRL+C to terminate the web-server'
    while running:
        httpServer.handle_request()
except KeyboardInterrupt:
    # CTRL+C exit
    print '\nUser shutdown'
finally:
    # Turn the motors off under all scenarios
    # PBR.MotorsOff()
    GPIO.cleanup() 
    print 'Motors off'
# Tell each thread to stop, and wait for them to end
running = False
#captureThread.join()
processor.terminated = True
watchdog.terminated = True
processor.join()
watchdog.join()
#del camera
# PBR.SetLed(True)
print 'Web-server terminated.'
