#-*- coding: utf-8 -*-
from gevent import pywsgi, sleep

from jtalk import jtalk
import picam
import pigpio
from datetime import datetime

class ChatCommander(object):
    def __init__(self):
        self.commands = {}
        self.elaborate()

    def elaborate(self):
        self.commands['say']   = self.say
        self.commands['sleep'] = self.sleep_
        self.elaborateRaspyGpio()
        self.commands['cheez'] = self.cheez
        self.commands['echo']  = self.echo
        self.commands['oreore'] = self.oreore

    def setMessageFunction(self, msg_func):
        self.msg_func = msg_func

    def showMessage(self, message):
        self.msg_func(message)

    def run(self, source):
        self.messages  = []

        lst = [tok.strip() for tok in source.split(';')]
        username = lst[0]
        filters  = [tok for tok in lst[1:] if len(tok) != 0 and tok[0] == '#']
        cmdlist  = [tok for tok in lst[1:] if len(tok) != 0 and tok[0] == '!']

        for cmd in cmdlist:
            tokens = cmd[1:].split(' ')
            self.execCommand(tokens[0], tokens[1:], username, filters)

    def execCommand(self, cmd, params, username, filters):
        try:
            self.commands[cmd](params, username, filters)
            print 'exec command "%s" by %s' % (cmd, username)
        except KeyError:
            pass
        except:
            self.showMessage('(%s) ERROR (params:%s)' % (cmd.upper(), params))


    #------------------------------------------------------------
    # say command
    #------------------------------------------------------------

    def say(self, params, username, filters):
        jtalk(' '.join(params))

    #------------------------------------------------------------
    # echo command
    #------------------------------------------------------------

    def echo(self, params, username, filters):
        header_str = ';'.join([username] + filters)
        self.showMessage('%s;%s' % (header_str,' '.join(params)))

    #------------------------------------------------------------
    # oreore command
    #------------------------------------------------------------

    def oreore(self, params, username, filters):
        header_str = ';'.join(["%s'" % params[0]] + filters)
        self.showMessage('%s;%s' % (header_str,' '.join(params[1:])))


    #------------------------------------------------------------
    # sleep command
    #------------------------------------------------------------

    def sleep_(self, params, username, filters):
        sleep(int(params[0]))

    #------------------------------------------------------------
    # cheez command
    #------------------------------------------------------------

    def cheez(self, params, username, filters):
        jtalk('はいっチーーズ!')
        sleep(2)
        now = datetime.now() 
        fname = 'img/img%02dT%02d%02d%02d_%05d.jpg' % (now.day, now.hour, now.minute, now.second, now.microsecond)
        
        picam.shoot(fname)
        header_str = ';'.join(['(CHEEZ)'] + filters)
        self.showMessage('%s;<img src="%s">' % (header_str,fname))

    #------------------------------------------------------------
    # gpio command
    #------------------------------------------------------------

    def elaborateRaspyGpio(self):
        self.gpio_commander = pigpio.GPIOCommander()

        self.commands['wt'] = self.gpio_output
        self.commands['rd'] = self.gpio_input
        self.commands['ss'] = self.gpio_set_servo
        self.commands['sstart'] = self.gpio_servo_start
        self.commands['sstop']  = self.gpio_servo_stop

    def gpio_output(self, params, username, filters):
        self.gpio_commander.output(int(params[0]), int(params[1]))
        gpio.output(int(params[0]), int(params[1]))
        
    def gpio_input(self, params, username, filters):
        value = self.gpio_commander.input(int(params[0]))
        self.showMessage('(GPIO INPUT);pin%s = %s' % (params[0], value))

    def gpio_servo_start(self,params, username, filters):
        ch = int(params[0])
        self.gpio_commander.sv_start(ch)

    def gpio_servo_stop(self,params, username, filters):
        ch = int(params[0])
        self.gpio_commander.sv_stop(ch)

    def gpio_set_servo(self, params, username, filters):
        ch = int(params[0])
        dd = int(params[1])
        self.gpio_commander.sv_changeDutyCycle(ch, dd)
