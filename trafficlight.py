PERIOD_IN_SECS = 30

class TrafficLight(object):

    def __init__(self, position, delay=PERIOD_IN_SECS, initial_state='Green'):
        self.state = 1 if initial_state == 'Green' else 0
        self.position = position
        self.delay = delay

    def is_green(self, time):
        return bool((self.state + int(time / self.delay)) % 2)

    def pretty_print(self, time):
        return 'Light %s at %d' % (
            'ON' if self.is_green(time) else 'OFF', self.position
        )

    def __lt__(self, other):
        return self.position - other.position
