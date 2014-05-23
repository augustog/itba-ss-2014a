from car import Car
from bus_line import BusLine

class Bus(Car):

    max_people = 100

    def __init__(self, line, speed, people_carried):
        Car.__init__(self, line.start_position,
            line.end_position, 1, speed, people_carried)

    def pick_up_people(self, people):
        self.people_carried += people
