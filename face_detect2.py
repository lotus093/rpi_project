from picamera.array import PiRGBArray
from picamera import PiCamera
import time 
import cv2
import sys
import imutils


import sys
sys.path.append('/usr/lib/python3/dist-packages')

import curses

import RPi.GPIO as GPIO
import time

##stepper setup section
delaytime = 0.2/1000.0
steps_pitch = 10
steps_yaw = 5

move_ind_pin = 16 #on while moving
pwr_ind_pin  = 13 #on while steppers powered
pit_dir_pin  = 19 #pitch direction pin
pit_step_pin = 26 #pitch step pin
yaw_dir_pin  = 20 #yaw direction pin
yaw_step_pin = 21 #yaw step pin
laser_pin    = 12 #laser pin

ydeadband = 2
xdeadband = 2
xgain = 4
ygain = 4

GPIO.setmode(GPIO.BCM)




# Create the haar cascade
profileCascade = cv2.CascadeClassifier("lbpcascade_profileface.xml")
faceCascade = cv2.CascadeClassifier("lbpcascade_frontalface_improved.xml")

font = cv2.FONT_HERSHEY_SIMPLEX

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (160, 120)
camera.framerate = 13

time.sleep(1)
camera.iso = 800
camera.shutter_speed = 0
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=camera.resolution)

# capture frames from the camera

def main():
    
    GPIO.setup(pwr_ind_pin, GPIO.OUT)
    GPIO.setup(move_ind_pin, GPIO.OUT)
    GPIO.setup(laser_pin, GPIO.OUT)
    GPIO.setup(pit_dir_pin, GPIO.OUT)
    GPIO.setup(pit_step_pin, GPIO.OUT)
    GPIO.setup(yaw_dir_pin, GPIO.OUT)
    GPIO.setup(yaw_step_pin, GPIO.OUT)

    GPIO.output(laser_pin,0)


    #start execution 
    GPIO.output(pwr_ind_pin,1)
    print("Steppers enabled")
    
    xctr = camera.resolution[0]/2
    yctr = camera.resolution[1]/2
    print("resx: ", xctr, " resy: ", yctr)

    
    # allow the camera to warmup
    time.sleep(0.1)
    lastTime = time.time()*1000.0
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(5, 15), flags = cv2.CASCADE_SCALE_IMAGE)
      
        #if no frontal faces, check for profile faces
        if faces == ():
            faces = profileCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(5, 15), flags = cv2.CASCADE_SCALE_IMAGE)
        
        #clear screen
        #print("\033c",end="")
        print("{a:.3f} ms elapsed. Found {b}".format(a=(time.time()*1000.0-lastTime),b=len(faces)))
        lastTime = time.time()*1000.0
        # Draw a circle around the faces
        for (x, y, w, h) in faces:
            xloc = int(x+w/2)
            yloc = int(y+h/2)
            cv2.circle(image, (xloc, yloc), int((w+h)/3), (255, 0, 0), 1)
            cv2.putText(image, "({a:d}, {b:d})".format(a=xloc,b=yloc),(xloc,yloc),font,0.5,(255,0,0),2,cv2.LINE_AA) 
            print("x: ",int(x+w/2), "y: ", int(y+h/2))
            
            #motion
            if abs(yloc - yctr) > ydeadband:
                move(delaytime, -1*int((yloc - yctr)*ygain), pit_dir_pin, pit_step_pin)
            if abs(xloc - xctr) > xdeadband:
                move(delaytime, -1*(int(xloc - xctr)*xgain), yaw_dir_pin, yaw_step_pin)


        

        # show the frame
        image = cv2.resize(image, (800,600))
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF
     
            # clear the stream in preparation for the next frame
        rawCapture.truncate(0)
        
            # if the `q` key was pressed, break from the loop
        if key == ord('q'):
            leave()
            break
        elif key == ord('l'):
            laser(1)
        elif key == ord('o'):
            laser(0)

def move(delay, stepnum, dir_pin, step_pin):
  if stepnum > 0:
    dirval = 1
  else:
    dirval = 0
    stepnum = -1* stepnum
    
  GPIO.output(move_ind_pin,1)
  for i in range(0, stepnum):
    GPIO.output(dir_pin, dirval)
    GPIO.output(step_pin, 1)
    time.sleep(delay)
    GPIO.output(step_pin, 0)
    time.sleep(delay)
  GPIO.output(move_ind_pin,0)
  
def laser(signal):
    if signal > 0:
        sig = 1
    else:
        sig = 0
    GPIO.output(laser_pin,sig)
  
def leave():
    print('Exiting')
    GPIO.output(pwr_ind_pin,0)
    GPIO.cleanup()
 
if __name__ == '__main__':
    main()
    
        

