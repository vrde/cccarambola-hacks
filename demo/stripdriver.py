import serial
from random import randint, random

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

    def __repr__(self):
        return '<{0}, {1}, {2}>'.format(self.r, self.g, self.b)
    
    def __nonzero__(self):
        return self.r or self.g or self.b

class Driver(object):

    def __init__(self, serial=None, factor=0.5, length=32):
        if serial is None:
            serial = serial.Serial('/dev/ttyUSB0', 115200,
                    xonxoff=0, rtscts=0, timeout=None)

        self.serial = serial
        self.factor = factor
        self.length = length
        self.strip = deque(Color(0, 0, 0) for i in range(length))

    def render(self):
        f = self.factor
        self.serial.write('\254') #SYNC
        for c in self.strip:
            self._write(chr(int(c.r * f)))
            self._write(chr(int(c.g * f)))
            self._write(chr(int(c.b * f)))

    def __setitem__(self, pos, val):
        assert len(val) == 3
        self.strip[pos].r = val[0]
        self.strip[pos].g = val[1]
        self.strip[pos].b = val[2]

    def _write(self, char):
        if char == '\254':
            char = '\255'
        self.serial.write(char)

    def shift(self, n):
        self.strip.rotate(n)

if __name__ == '__main__':
    s = serial.Serial('/dev/ttyS1', 115200, xonxoff=0, rtscts=0, timeout=None)
    d = Driver(serial=s, factor=0.05)
    
    d.strip[0].r = 255
    
    c = 0
    
    while True:
        if random() <= 0.1:
            if random() < 0.5:
                kill = randint(0, 31)
                if d.strip[kill]:
                    d.strip[kill] = Color(0, 0, 0)
            else:
                spawn = randint(0, 31)
                if not d.strip[spawn]:
                    d.strip[spawn] = Color(255, 0, 0)
        d.shift(1)
        d.render()

