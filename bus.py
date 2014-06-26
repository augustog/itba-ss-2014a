import math
import random

from car import Car

class Bus(Car):
    max_people = 100
    length = 8

    def __init__(self, line, speed, people_carried):
        self.line = line
        self.just_stopped = False
        Car.__init__(self, 0, 0, 1, speed, people_carried)

    def pick_up_people(self, people):
        self.people_carried += people

    def people_leave(self):
        number = int(math.floor(random.random() * random.random() / 7 * self.people_carried))
        print 'Number of people leaving: %d' % number
        self.people_carried -= number
        return number

    def distance_to_target_position(self):
        distances = []
        for stop in self.line.bus_stops:
            distance = stop.position - self.position
            if distance > 0:
                distances.append(distance)
        if distances:
            return min(distances)
        return 10000000
