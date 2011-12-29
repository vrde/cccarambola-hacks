from serial import Serial
from random import randint, random
from itertools import chain

from collections import deque

r = '\x10\x00\x00'
g = '\x00\x10\x00'
b = '\x00\x00\x10'
w = '\x10\x10\x10'
k = '\x00\x00\x00'

class Color(object):
    __slots__ = ('r', 'g', 'b')

    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def __getitem__(self, pos):
        if pos == 0:
            return self.r
        if pos == 1:
            return self.g
        if pos == 2:
            return self.b

    def __setitem__(self, pos, val):
        if pos == 0:
            self.r = val
        if pos == 1:
            self.g = val
        if pos == 2:
            self.b = val

    def __repr__(self):
        return '<{0}, {1}, {2}>'.format(self.r, self.g, self.b)
    
    def __nonzero__(self):
        return self.r or self.g or self.b

class Strip(deque):
    def __setitem__(self, pos, val):
        if not isinstance(val, Color):
            val = Color(*val)
        deque.__setitem__(self, pos, val)

class Driver(object):

    def __init__(self, serial=None, factor=0.5, length=32, substrips=1):

        if serial is None:
            serial = Serial('/dev/ttyUSB0', 115200,
                    xonxoff=0, rtscts=0, timeout=None)

        elif isinstance(serial, basestring):
            serial = Serial(serial, 115200,
                    xonxoff=0, rtscts=0, timeout=None)

        self.serial = serial
        self.factor = factor
        self.length = length
        self.strips = []

        if isinstance(substrips, int):
            size = length / substrips
            substrips = (size, ) * substrips

        for s in substrips:
            self.strips.append(
                Strip([Color(0, 0, 0) for i in range(s) ],
                    maxlen=s))

    def render(self):
        f = self.factor
        self.serial.write('\254') #SYNC
        for c in chain(*self.strips):
            self._write(chr(int(c.r * f)))
            self._write(chr(int(c.g * f)))
            self._write(chr(int(c.b * f)))

    def __getitem__(self, pos):
        return self.strips[0][pos]

    def __setitem__(self, pos, val):
        self.strips[0][pos] = val

    def _write(self, char):
        if char == '\254':
            char = '\255'
        self.serial.write(char)

    def shift(self, n):
        self.strips[0].rotate(n)

    def pushl(self, c):
        self.strips[0].appendleft(c)

    def pushr(self, c):
        self.strips[0].append(c)

def demo2(s):
    d = Driver(serial=s, factor=0.05, substrips=(6, 4, 26))

    for s in d.strips:
        s.appendleft(Color(255, 0, 0))

    while True:
        time.sleep(0.01)
        for s in d.strips:
            s.rotate(1)
            d.render()
            
if __name__ == '__main__':
    import sys, time

    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        sys.exit('usage: stripdriver.py /dev/<tty-usb>')

    s = Serial(port, 115200, xonxoff=0, rtscts=0, timeout=None)
    demo2(s)
    d = Driver(serial=s, factor=0.05)
    
    d[0] = (255, 0, 0)
    
    c = 0

    while True:
        time.sleep(0.001)
        if random() <= 0.1:
            if random() < 0.5:
                kill = randint(0, 31)
                if d[kill]:
                    #d.strip[kill] = Color(0,0,255)
                    #d.render()
                    d[kill] = Color(0, 0, 0)
            else:
                spawn = randint(0, 31)
                if not d[spawn]:
                    r = random()
                    g = random()
                    b = random()
                    factor = r + g + b
                    #factor = 1
                    r = int(r / factor * 255.)
                    g = int(g / factor * 255.)
                    b = int(b / factor * 255.)
                    #d.strip[spawn] = Color(0 ,255, 0)
                    #d.render()
                    d[spawn] = Color(r, g, b)
        d.shift(1)
        d.render()
