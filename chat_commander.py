#-*- coding: utf-8 -*-
from gevent import pywsgi, sleep

            
import RPi.GPIO as gpio
from jtalk import jtalk
import picam
from datetime import datetime

class ChatCommander(object):
    def __init__(self):
        self.commands = {}
        self.elaborate()

    def elaborate(self):
        self.commands['say']   = self.say
        self.commands['sleep'] = self.mysleep
        self.elaborateRaspyGpio()
        self.commands['cheez'] = self.cheez

    def setMessageFunction(self, msg_func):
        self.msg_func = msg_func

    def showMessage(self, message):
        self.msg_func(message)

    def run(self, source):
        self.messages  = []

        lst = [tok.strip() for tok in source.split(';')]
        self.username = lst[0]
        self.filters  = [tok for tok in lst[1:] if tok[0] == '#']
        cmdlist  = [tok for tok in lst[1:] if tok[0] == '!']

        for cmd in cmdlist:
            tokens = cmd[1:].split(' ')
            self.execCommand(tokens[0], tokens[1:])

    def execCommand(self, cmd, params):
        try:
            self.commands[cmd](params)
            print 'exec command "%s" by %s' % (cmd, self.username)
        except KeyError:
            pass
        except:
            self.showMessage('(%s) ERROR (params:%s)' % (cmd.upper(), params))


    #------------------------------------------------------------
    # say command
    #------------------------------------------------------------

    def say(self, params):
        jtalk(' '.join(params))

    #------------------------------------------------------------
    # sleep command
    #------------------------------------------------------------

    def mysleep(self, params):
        sleep(int(params[0]))

    #------------------------------------------------------------
    # cheez command
    #------------------------------------------------------------

    def cheez(self, params):
        jtalk('はいっチーーズ!')
        sleep(2)
        now = datetime.now() 
        fname = 'img/img%02dT%02d%02d%02d_%05d.jpg' % (now.day, now.hour, now.minute, now.second, now.microsecond)
        
        picam.shoot(fname)
        header_str = ';'.join(['(CHEEZ)'] + self.filters)
        self.showMessage('%s;<img src="%s">' % (header_str,fname))

    #------------------------------------------------------------
    # gpio command
    #------------------------------------------------------------

    def elaborateRaspyGpio(self):
        gpio.setmode(gpio.BOARD) # or gpio.BOARD
        gpio.setup(11, gpio.OUT)  
        # gpio.setup(22, gpio.IN)  

        self.commands['wt'] = self.gpio_output
        self.commands['rd'] = self.gpio_input

    def gpio_output(self, params):
        gpio.output(int(params[0]), int(params[1]))
        
    def gpio_input(self, params):
        value = gpio.output(int(params[0]))
        self.showMessage('(GPIO INPUT);pin%s = %s' % (params[0], value))



