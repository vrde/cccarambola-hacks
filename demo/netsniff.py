# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 23:49:16 2011

@author: kiwi
"""

from stripdriver import Driver, Color
from subprocess import Popen, PIPE
import threading
from collections import deque
from math import modf
import time
from datetime import datetime
from array import array
now = datetime.now

# iw phy phy0 interface add mon0 type monitor

IF = 'wmon0'
#IF = 'wlan0'
DEV = '/dev/ttyS1'
#DEV = '/dev/ttyUSB0'
SAMPLES = 128
LEDS = 8
ROTATE_SLEEP_INTVL = 0.05
SAMPLE_INTVL = 0.05
#LED_ROTATE_INTV = 0.1
REFRESH_INTVL = 0.1

statlock = threading.Lock()

#Counter = lambda : [0,0,0]
Counter = lambda : array("I", (0,0,0))
#Counter = lambda: [0,0,0]

class TrafficTypes:
    http = 0
    https = 1
    other = 2

p = Popen(['tcpdump', '-ni', IF, 'tcp'], bufsize=80,
                     stdin=PIPE, stdout=PIPE, close_fds=True)
stdout = p.stdout
stats = deque()
for i in range(SAMPLES):
    stats.append(Counter())
driver = Driver(DEV, substrips=4)


def get_one():
    l = stdout.readline()
    if '.80 ' in l:
        return TrafficTypes.http
    elif '.443 ' in l:
        return TrafficTypes.https
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
            led = (float(LEDS) * i) / SAMPLES
            factor, _ = modf(led)
            factor = factor * 2
            led = int(led)
            if factor > 1:
                factor = 2 - factor
            if led != cled:
                r, g, b = 0., 0., 0.
                cled = led
            r += s[TrafficTypes.https] * factor
            g += s[TrafficTypes.http] * factor
            b += s[TrafficTypes.other] * factor
            maxv = max(max((r,g,b)), maxv)
            driver.strips[TrafficTypes.http][cled] = Color(r * 255 / maxv, 0, 0)
            driver.strips[TrafficTypes.https][cled] = Color(0, g * 255 / maxv, 0)
            driver.strips[TrafficTypes.other][cled] = Color(0, 0, b * 255 / maxv)
            #driver[cled] = (r * 255 / maxv , g * 255 / maxv, b * 255 / maxv)

        for s in driver.strips:
            s[0] = Color(32, 16, 0)
        driver.render()

def main():
        rotatort = threading.Thread(target=rotator, args=(stats, ROTATE_SLEEP_INTVL))
        statst = threading.Thread(target=stats_updater, args=(stats,))
        rotatort.daemon = True
        statst.daemon = True
        rotatort.start()
        statst.start()
        while 1:
            time.sleep(REFRESH_INTVL)
            render()

main()
