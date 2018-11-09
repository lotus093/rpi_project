import sys
sys.path.append('/usr/lib/python3/dist-packages')



import RPi.GPIO as GPIO
import time
 
GPIO.setmode(GPIO.BCM)
delaytime = 1.0/1000.0 

active_pin = 16
rst_pin = 13
dir_pin = 19
step_pin = 26
 
GPIO.setup(rst_pin, GPIO.OUT)
GPIO.setup(dir_pin, GPIO.OUT)
GPIO.setup(step_pin, GPIO.OUT)
GPIO.setup(active_pin, GPIO.OUT)
 
GPIO.output(rst_pin,1)
print("Steppers enabled")
 
def forward(delay, steps):
  GPIO.output(active_pin,1)
  for i in range(0, steps):
    GPIO.output(dir_pin, 1)
    GPIO.output(step_pin, 1)
    time.sleep(delay)
    GPIO.output(step_pin, 0)
    time.sleep(delay)
  GPIO.output(active_pin,0)
 
def backwards(delay, steps):
  GPIO.output(active_pin,1)
  for i in range(0, steps):
    GPIO.output(dir_pin, 0)
    GPIO.output(step_pin, 1)
    time.sleep(delay)
    GPIO.output(step_pin, 0)
    time.sleep(delay)
  GPIO.output(active_pin,0)
 
while True:
  steps = input("How many steps forward? ")
  forward(delaytime, int(steps))
  steps = input("How many steps backwards? ")
  backwards(delaytime,  int(steps))
  leave = input("Exit?")
  if (leave == "1"):
      GPIO.output(rst_pin,0)
      GPIO.cleanup() 
      break
    
