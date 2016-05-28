#-*- coding: utf-8 -*-

import picamera

def shoot(fname):
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.capture(fname)
