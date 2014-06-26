class BusLine(object):

    def __init__(self, bus_stops, frequency):
        self.bus_stops = bus_stops
        self.frequency = frequency
        self.last_time_appeared = 0
