import bus
import random

class BusLine(object):

    def __init__(self, bus_stops, frequency):
        self.bus_stops = bus_stops
        self.frequency = frequency
        self.last_time_appeared = 0

    def new_bus(self):
        return bus.Bus(self, 0, random.randint(0, bus.Bus.max_people))
