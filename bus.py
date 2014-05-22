from car import Car
from bus_line import BusLine

class Bus(Car):
    max_people = 100
    length = 8

    def __init__(self, line, speed, people_carried):
        self.line = line
        Car.__init__(self, 0, 0, speed, people_carried)

    def pick_up_people(self, people):
        self.people_carried += people
