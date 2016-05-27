#-*- coding: utf-8 -*-
from gevent import pywsgi, sleep

            
#import Rpi.GPIO as gpio

class ChatCommander(object):
    def __init__(self):
        self.commands = {}
#        self.message  = []
        self.elaborate()

    def elaborate(self):
        self.commands['say']   = self.say
        self.commands['sleep'] = self.mysleep
#        self.elaborateRaspyGpio()

    def set_message_function(self, msg_func):
        self.msg_func = msg_func

    def show_message(self, message):
        self.msg_func(message)

    def run(self, source):
        self.messages  = []

        lst = source.split(';')
        print lst
        self.username = lst[0]
        stmlist  = lst[1:]

        for stm in stmlist:
            if len(stm) != 0 and stm[0] != '!': continue
            tokens = stm[1:].split(' ')
            print 'T', tokens
            self.exec_command(tokens[0], tokens[1:])

    def exec_command(self, cmd, params):
        try:
            self.commands[cmd](params)
            print 'exec command "%s" by %s' % (cmd, self.username)
        except KeyError:
            pass
        except:
            self.show_message('(%s) ERROR (params:%s)' % (cmd.upper(), params))


    #------------------------------------------------------------
    # say command
    #------------------------------------------------------------

    def say(self, params):
        self.show_message( '(SAY); %s' % ' '.join(params))

    #------------------------------------------------------------
    # sleep command
    #------------------------------------------------------------

    def mysleep(self, params):
        sleep(int(params[0]))

    #------------------------------------------------------------
    # gpio command
    #------------------------------------------------------------

    def elaborateRaspyGpio(self):
        gpio.setup()
        gpio.setmode(gpio.BCN) # or gpio.BOARD
        # gpio.setup(21, gpio.OUT)  
        # gpio.setup(22, gpio.IN)  

        self.commands['wt'] = self.gpio_output
        self.commands['rd'] = self.gpio_input

    def gpio_output(self, params):
        gpio.output(int(params[0]), int(params[1]))
        
    def gpio_input(self, params):
        value = gpio.output(int(params[0]))
        self.show_message('(GPIO INPUT);pin%s = %s' % (params[0], value))



