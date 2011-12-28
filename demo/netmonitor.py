import json
import time
from urllib import urlopen
from stripdriver import Driver
import logging

from collections import deque

log = logging.getLogger()

ENDPOINT = 'http://dashboard.congress.ccc.de/current.json'

mapping = [0, 1, 1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 9, 11, 14, 18, 22, 27,
           34, 43, 53, 67, 84, 104, 131, 163, 204, 255]
mapping_len = len(mapping) - 1

class NetworkDriver(Driver):
    def __init__(self, serial=None, factor=0.5, length=32):
        Driver.__init__(self, serial=serial, factor=factor, length=length)
        self.upvalues = deque(maxlen=(length - 2) / 2)
        self.downvalues = deque(maxlen=(length - 2) / 2)

    def _push_value(self, v, q):
        r = []
        q.appendleft(v)
        mx = max(q)
        mn = min(q)

        print 'recv: ', v, ' | ', '\t',
        for i, v in enumerate(q):
            if mx == mn:
                normalized = mapping_len
            else: 
                normalized = int(mapping_len * ((v - mn) / float(mx - mn)))
            r.append(mapping[normalized])
            print normalized,

        print
        print '\t\t\t',
        for v in q:
            print v,
        print
        return r

    def push_upstream(self, v):
        return self._push_value(v, self.upvalues)

    def push_downstream(self, v):
        return self._push_value(v, self.downvalues)

    def render(self):
        Driver.render(self)

    def push_down(self):
        pass

class NetworkRenderer(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.driver = NetworkDriver()
        self.normalized_upstream = None
        self.normalized_downstream = None

    def _fetch(self):
        data = None
        try:
            f = urlopen(self.endpoint)
            data = json.loads(f.read())
        except Exception, e:
            log.exception(e)
        return data

    def merge(self, a, b):
        for i, v in enumerate(a):
            self.driver.strip[i + 1].r = v
        self.driver.strip[0].b = 255

        for i, v in enumerate(b):
            self.driver.strip[self.driver.length / 2 + i + 1].g = v
        self.driver.strip[16].b = 255


    def run(self):
        while True:
            data = self._fetch()
            if not data: continue
            log.debug('got new data')

            self.merge(
                self.driver.push_upstream(int(data['bw']['up'])),
                self.driver.push_downstream(int(data['bw']['down'])))

            time.sleep(4)
            self.driver.render()

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s %(module)-15s %(levelname)-8s %(message)s',
        level=logging.DEBUG)

def main():
    setup_logging()
    nr = NetworkRenderer(ENDPOINT)
    nr.run()

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 2:
        port = sys.argv[1]
    else:
        sys.exit('usage: stripdriver.py /dev/<tty-usb>')

    d = Driver(serial=port, factor=0.05)
    main()

