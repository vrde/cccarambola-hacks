import serial
from random import randint, random


from collections import deque

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
    def __init__(self, s, factor=1, length=32):
        self.serial = s
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

    def _write(self, char):
        if char == "\254":
            char = "\255"
        self.serial.write(char)

        
        

    def shift(self, n):
        self.strip.rotate(n)

if __name__ == "__main__":
    
    
    scale = 64
    
    r = '\x10\x00\x00'
    g = '\x00\x10\x00'
    b = '\x00\x00\x10'
    w = '\x10\x10\x10'
    k = '\x00\x00\x00'
    
    s = serial.Serial('/dev/ttyS1', 115200, xonxoff=0, rtscts=0, timeout=None)
    # = ''.join(chr(randint(0, 16)) for i in range(3 * 32))
    #o = b + k * 31
    d = Driver(s, factor=0.05)
    
    import time
    
    d.strip[0].r = 255
    
    c = 0
    
    while True:
        #time.sleep(0.05)
        if random() <= 0.1:
            if random() < 0.5:
                kill = randint(0, 31)
                if d.strip[kill]:
                    #d.strip[kill] = Color(0,0,255)
                    #d.render()
                    d.strip[kill] = Color(0, 0, 0)
            else:
                spawn = randint(0, 31)
                if not d.strip[spawn]:
                    #d.strip[spawn] = Color(0 ,255, 0)
                    #d.render()
                    d.strip[spawn] = Color(255, 0, 0)
        print "shift"
        d.shift(1)
        d.render()
