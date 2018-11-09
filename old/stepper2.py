import sys
sys.path.append('/usr/lib/python3/dist-packages')

import curses

import RPi.GPIO as GPIO
import time
 

delaytime = 0.2/1000.0
steps_pitch = 10
steps_yaw = 5

move_ind_pin = 16 #on while moving
pwr_ind_pin = 13      #on while steppers powered
pit_dir_pin = 19 #pitch direction pin
pit_step_pin = 26 #pitch step pin
yaw_dir_pin = 20 #yaw direction pin
yaw_step_pin = 21 #yaw step pin
laser_pin = 12 #laser pin

GPIO.setmode(GPIO.BCM)

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
 

def main(window):
    
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
      
  
    while True:
        key = window.getch()
        if key == ord('w'):
            move(delaytime, steps_pitch, pit_dir_pin, pit_step_pin)
        elif key == ord('s'):
            move(delaytime, -1*steps_pitch, pit_dir_pin, pit_step_pin)
        elif key == ord('a'):
            move(delaytime, steps_yaw, yaw_dir_pin, yaw_step_pin)
        elif key == ord('d'):
            move(delaytime, -1*steps_yaw, yaw_dir_pin, yaw_step_pin)
        elif key == ord('l'):
            laser(1)
        elif key == ord('o'):
            laser(0)            
        elif key == ord('q'):
            leave()
            break

           
if __name__ == '__main__':
    curses.wrapper(main) 