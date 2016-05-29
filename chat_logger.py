#-*- coding: utf-8 -*-
import datetime

class ChatLogger(object):
    '''
    Userと同じインターフェイス(receiveを除く)を実装する。
    ファイル出力中はアプリケーションをロックしてしまうので、
    ユーザ体験の問題が出る場合はロギングスレッドを立てること。
    '''

    def __init__(self, fname):
        self.logfile = open(fname,'a')
        now = datetime.datetime.now()
        self.send('start! %0d-%02d-%02d' % (now.year, now.month, now.day))

    def send(self, msg):
        now = datetime.datetime.now()
        self.logfile.write('%02d:%02d:%02d;%s\n' %
                           (now.hour, now.minute, now.second, msg))
        self.logfile.flush()

