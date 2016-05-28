# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime
import threading
import os

def jtalk(msg):
    th = threading.Thread(target=jtalk_proc, args=(msg,))
    th.start()


def jtalk_proc(msg):
    now = datetime.now()
    fname = 'say%02dT%02d%02d%02d_%03d.wav' % (now.day, now.hour, now.minute, now.second, now.microsecond)

    cmd = ['open_jtalk',
           '-x', '/var/lib/mecab/dic/open-jtalk/naist-jdic',
           '-m', '/usr/share/hts-voice/mei/mei_normal.htsvoice', # voice
           '-r', '1.0',                                          # speed
           '-ow', fname]

    c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    c.stdin.write(msg)
    c.stdin.close()
    c.wait()

    a = subprocess.Popen(['aplay', '-q', fname])
    a.wait()
    os.remove(fname)

if __name__ == '__main__':
    jtalk(u'ゆっくりしていってね！'.encode('utf-8'))
    
