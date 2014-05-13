
class TrafficLight(object):
    period_in_secs = 30

    def __init__(self, position, initial_state = 'Green'):
        self.state = 1 if initial_state == 'Green' else 0
        self.position = position

    def is_green(self, time):
        return bool((self.state + int(time / 30)) % 2)

    def pretty_print(self, time):
        return 'Light %s at %d' % (
            'ON' if self.is_green(time) else 'OFF', self.position
        )
