# -*- coding: utf-8 -*-

import subprocess
from datetime import datetime

def jtalk(msg):
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

    subprocess.Popen(['aplay', '-q', fname])
        

if __name__ == '__main__':
    jtalk(u'ゆっくりしていってね！'.encode('utf-8'))
    
