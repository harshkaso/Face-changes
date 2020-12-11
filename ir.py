import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17,GPIO.IN)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)

try:
    
    while True:
        if GPIO.input(17) == 1:
            print("Motion Detected")
            GPIO.output(26,GPIO.HIGH)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(12,GPIO.LOW)
            
            
        else:
            print("Motion not Detected")
            GPIO.output(26,GPIO.LOW)
            GPIO.output(16,GPIO.HIGH)
            GPIO.output(12,GPIO.HIGH)
except KeyboardInterrupt:
    GPIO.cleanup()
