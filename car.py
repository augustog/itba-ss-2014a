import math

ADVANCE = 'Avanzando'
CHANGING_LANE = 'Cambiando de carril'

class Car(object):
    max_speed = 15
    acceleration = 1.5
    length = 3

    def __init__(self, position, exit_road, speed, people_carried):
        self.position = position
        self.exit_road = exit_road
        self.speed = speed
        self.people_carried = people_carried
        self.state = ADVANCE

    def is_first_on_traffic_light(self):
        return math.floor(self.position) == self.position \
                and int(self.position) % 100 == 0

    def advance(self, delta_time):
        self.halted_on_light = False
        # TODO: Move the car according to speed and time and neighbours
