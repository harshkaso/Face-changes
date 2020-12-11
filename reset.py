import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(16,GPIO.OUT)
GPIO.setup(26,GPIO.OUT)
GPIO.setup(12,GPIO.OUT)
GPIO.cleanup()