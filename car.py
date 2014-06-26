import math

import source

ADVANCE = 'Avanzando'
CHANGING_LANE = 'Cambiando de carril'

class Car(object):
    max_speed = 15
    max_acceleration = 1.5
    length = 3

    def __init__(self, position, exit_road, blocks_before_turn,
            speed, people_carried):
        self.position = position
        self.start_time = 0
        self.exit_road = exit_road
        self.blocks_before_turn = blocks_before_turn
        self.speed = speed
        self.people_carried = people_carried
        self.state = ADVANCE
        self.change_lane = source.Source(1)
        self.last_delta = 0

    def set_acceleration(self, acceleration, delta_time):
        self.acceleration = acceleration
        self.speed += acceleration * delta_time
        if self.speed < 0:
            self.speed = 0
        self.speed = min(self.speed, self.max_speed)

    def advance(self, delta_time):
        self.last_delta = self.speed * delta_time
        self.position += self.speed * delta_time

    def _get_target_acceleration(self, target_speed, distance):
        if distance == 0:
            return 0
        return (math.pow(target_speed, 2) - math.pow(self.speed, 2)) / (
            2 * distance)

    # TODO: Change name if better name found
    def acceleration_to_reach(self, target_speed, distance, delta_time):
        return self._get_target_acceleration(target_speed, distance)

    def __str__(self):
        return 'Car(position=%.2f, speed=%.2f)' % (
            self.position,
            self.speed
        )

    def distance_to_target_position(self):
        if not self.exit_road:
            return 1000000
        return self.exit_road * 100 - self.position
