# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 23:49:16 2011

@author: kiwi
"""

from stripdriver import Driver
from subprocess import Popen, PIPE
import threading
from collections import deque
import time
from datetime import datetime
now = datetime.now

IF = 'wmon0'
#IF = 'wlan0'
DEV = '/dev/ttyS1'
#DEV = '/dev/ttyUSB0'
SAMPLES = 512
LEDS = 32
ROTATE_SLEEP_INTVL = 0.05
SAMPLE_INTVL = 0.05
#LED_ROTATE_INTV = 0.1
REFRESH_INTVL = 0.05

statlock = threading.Lock()

Counter = lambda :[0,0,0]

class TrafficTypes:
    http = 0
    https = 1
    other = 2

p = Popen(['tcpdump', '-ni', IF, 'tcp'], bufsize=100,
                     stdin=PIPE, stdout=PIPE, close_fds=True)
stdout = p.stdout
stats = deque()
for i in range(SAMPLES):
    stats.append(Counter())
driver = Driver(DEV)


def get_one():
    l = stdout.readline()
    if '.80 ' in l:
        return TrafficTypes.https
    elif '.443 ' in l:
        return TrafficTypes.http
    else:
        return TrafficTypes.other


def rotator(stats, interval):
    while True:
        print "rotation"
        time.sleep(interval)
        with statlock:
            stats.popleft()
            stats.append(Counter())

def stats_updater(stats):
    while True:
        print "stats update"
        p = get_one()
        with statlock:
            stats[-1][p] += 1

def render():
    with statlock:
        print "rendering"
        cled = 0
        r,g,b = 0,0,0
        maxv = 255
        for i, s in enumerate(stats):
            led = (LEDS * i) / SAMPLES
            if led != cled:
                r, g, b = 0, 0, 0
                cled = led
            r += s[TrafficTypes.https]
            g += s[TrafficTypes.https]
            b += s[TrafficTypes.other]
            maxv = max(max((r,g,b)), maxv)
            driver[cled] = (r * 255 /maxv , g * 255 / maxv, b * 255 / maxv)
        driver.render()

def main():
        rotatort = threading.Thread(target=rotator, args=(stats, ROTATE_SLEEP_INTVL))
        statst = threading.Thread(target=stats_updater, args=(stats, SAMPLE_INTVL))
        rotatort.daemon = True
        statst.daemon = True
        rotatort.start()
        statst.start()
        while 1:
            time.sleep(REFRESH_INTVL)
            render()

main()