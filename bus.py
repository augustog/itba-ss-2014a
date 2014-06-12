from car import Car
from bus_line import BusLine

class Bus(Car):
    max_people = 100
    length = 8
    _in = 0

    def __init__(self, line, speed, people_carried):
        self.line = line
        self.__class__._in += 1
        self.index = self.__class__._in
        Car.__init__(self, 0, 0, 1, speed, people_carried)

    def pick_up_people(self, people):
        self.people_carried += people

    def distance_to_target_position(self):
        distances = []
        for stop in self.line.bus_stops:
            distance = stop.position - self.position
            if distance > 0:
                distances.append(distance)
        if distances:
            return min(distances)
        return 10000000
