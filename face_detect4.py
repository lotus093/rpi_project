from picamera.array import PiRGBArray
from picamera import PiCamera
import time 
import cv2
import sys
import imutils


import sys
sys.path.append('/usr/lib/python3/dist-packages')

import time

import pigpio


def move(stepfreq, dir_pin, step_pin, maxPWMfreq):
  if stepfreq > 0:
    pi.write(dir_pin, 1)
    cycle = 50
  elif stepfreq == 0:
    cycle = 0
  else: #moving in negative
    pi.write(dir_pin, 0)
    stepfreq = abs(stepfreq)
    cycle = 50

  if stepfreq > maxPWMfreq:
      stepfreq = maxPWMfreq
  pi.set_PWM_frequency(step_pin, stepfreq)
  pi.set_PWM_dutycycle(step_pin, cycle)    

det_ind_pin = 16 #on when face found
pwr_enb_pin  = 13 #on while steppers powered
pit_dir_pin  = 19 #pitch direction pin
pit_step_pin = 26 #pitch step pin
yaw_dir_pin  = 20 #yaw direction pin
yaw_step_pin = 21 #yaw step pin
laser_pin    = 12 #laser pin

xdead = 4
ydead = 4

xgain = 30 #yaw
ygain = 20 #pitch

xmaxPWMfreq = 750 #max rate before stepper motor stall
ymaxPWMfreq = 4000
missed_face_cnt_max = 3

# Create the haar cascade
profileCascade = cv2.CascadeClassifier("lbpcascade_profileface.xml")
faceCascade = cv2.CascadeClassifier("lbpcascade_frontalface_improved.xml")

font = cv2.FONT_HERSHEY_SIMPLEX

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (208, 156)
#camera.zoom = (0,0,0.1,0.1)  #zoom won't work, still acquires at full res then crops
camera.framerate = 20

time.sleep(1)
camera.iso = 800
camera.shutter_speed = 30000
camera.exposure_mode = 'off'
rawCapture = PiRGBArray(camera, size=camera.resolution)

# set up pigpio GPIO
pi = pigpio.pi()
if not pi.connected:
  exit(0)

pi.set_mode(det_ind_pin,  pigpio.OUTPUT) 
pi.set_mode(pwr_enb_pin,  pigpio.OUTPUT) #on while steppers powered
pi.set_mode(pit_dir_pin,  pigpio.OUTPUT) #pitch direction pin
pi.set_mode(pit_step_pin, pigpio.OUTPUT) #pitch step pin
pi.set_mode(yaw_dir_pin,  pigpio.OUTPUT) #yaw direction pin
pi.set_mode(yaw_step_pin, pigpio.OUTPUT) #yaw step pin
pi.set_mode(laser_pin,    pigpio.OUTPUT) #laser pin

pi.set_PWM_range(pit_step_pin, 100)
pi.set_PWM_range(yaw_step_pin, 100)

move(0, yaw_dir_pin, yaw_step_pin, xmaxPWMfreq)
move(0, pit_dir_pin, pit_step_pin, ymaxPWMfreq)

def main():


    
    
    #start execution 
    pi.write(pwr_enb_pin,1)
    print("Steppers enabled")


    xctr = int(camera.resolution[0]/2)
    yctr = int(camera.resolution[1]/2)
    print("resx: ", xctr, " resy: ", yctr)

    
    # allow the camera to warmup
    time.sleep(0.1)
    lastTime = time.time()*1000.0
    
    missed_face_cnt = 0
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        # grab the raw NumPy array representing the image, then initialize the timestamp
        # and occupied/unoccupied text
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the image
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(3, 3), flags = cv2.CASCADE_SCALE_IMAGE)
      
        #if no frontal faces, check for profile faces
        if faces == ():
            faces = profileCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2, minSize=(3, 3), flags = cv2.CASCADE_SCALE_IMAGE)
        else:
            missed_face_cnt = 0
        
        
        if faces == (): #if still no faces, zero motion, turn off face light
            pi.write(det_ind_pin, 0)
            move(0, pit_dir_pin, pit_step_pin, ymaxPWMfreq) #don't keep pitching

            
            if missed_face_cnt > missed_face_cnt_max: #stop if haven't seen face in a while
                move(0, yaw_dir_pin, yaw_step_pin, xmaxPWMfreq)           
            
            missed_face_cnt = missed_face_cnt + 1
        else:
            pi.write(det_ind_pin,1)
            
        
        #clear screen
        #print("\033c",end="")
        print("{a:.3f} ms elapsed. Found {b}".format(a=(time.time()*1000.0-lastTime),b=len(faces)))
        lastTime = time.time()*1000.0
        # Draw a circle around the faces
        for (x, y, w, h) in faces:
            xloc = int(x+w/2)
            yloc = int(y+h/2)
            cv2.circle(image, (xloc, yloc), int((w+h)/3), (255, 0, 0), 1)
            cv2.putText(image, "({a:d}, {b:d})".format(a=xloc-xctr,b=yloc-yctr),(xloc,yloc),font,0.5,(255,0,0),2,cv2.LINE_AA) 
            print("x: ",int(x+w/2), "y: ", int(y+h/2))
            
            #motion
            y_stepfreq = -1*int((yloc - yctr))
            if abs(y_stepfreq) < ydead:
                y_stepfreq = 0
            move(y_stepfreq*ygain, pit_dir_pin, pit_step_pin, ymaxPWMfreq)
            
            x_stepfreq = -1*(int(xloc - xctr))
            if abs(x_stepfreq) < xdead:
                x_stepfreq = 0
            move(x_stepfreq*xgain, yaw_dir_pin, yaw_step_pin, xmaxPWMfreq)


        

        # show the frame
        #image = cv2.resize(image, (800,600))
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



  
def laser(signal):
    if signal > 0:
        sig = 1
    else:
        sig = 0
    pi.write(laser_pin,sig)
  
def leave():
    print('Exiting')
    camera.close()
    
    pi.write(pwr_enb_pin,0)
    pi.write(det_ind_pin, 0)
    pi.write(laser_pin, 0)

    pi.stop()
    
 
if __name__ == '__main__':
    main()
    
        

