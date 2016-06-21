#-*- coding:utf-8 -*-
import RPi.GPIO as gpio

class GPIOCommander(object):
    def __init__(self):
        gpio.setmode(gpio.BCM) # gpio.BCM or gpio.BOARD
        gpio.setup(11, gpio.OUT)  

        # elabrate servo
        self.servo = {}

        for servo_ch in [18,23]:
            gpio.setup(servo_ch, gpio.OUT)
            self.servo[servo_ch] = gpio.PWM(servo_ch, 50) # 50hz
            self.servo[servo_ch].start(0.0)
    
    def output(self, ch, value):
        gpio.output(ch, value)

    def input(self, ch):
        return gpio.input(ch)

    def changeDutyCycle(self, ch, dd):
        print 'ss ch=%d ,dd=%d,' % (ch, dd)
        self.servo[ch].ChangeDutyCycle(dd)

    def __del__(self):
        gpio.cleanup()



