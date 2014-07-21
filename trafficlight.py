PERIOD_IN_SECS = 30

class TrafficLight(object):

    def __init__(self, position, delay=PERIOD_IN_SECS):
        self.acc = 0
        self.position = position
        self.delay = delay

    def is_green(self, time):
        return int(self.acc + time) % (self.delay * 2) < self.delay

    def pretty_print(self, time):
        return 'Light %s at %d' % (
            'ON' if self.is_green(time) else 'OFF', self.position
        )

    def __lt__(self, other):
        return self.position - other.position
