import math

ADVANCE = 'Avanzando'
CHANGING_LANE = 'Cambiando de carril'

class Car(object):
    max_speed = 15
    max_acceleration = 1.5
    length = 3

    def __init__(self, position, exit_road, speed, people_carried):
        self.position = position
        self.exit_road = exit_road
        self.speed = speed
        self.people_carried = people_carried
        self.state = ADVANCE

    def set_acceleration(self, acceleration, delta_time):
        self.acceleration = acceleration
        self.speed += acceleration * delta_time
        if self.speed < 0:
            self.speed = 0
        self.speed = min(self.speed, self.max_speed)

    def advance(self, delta_time):
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
