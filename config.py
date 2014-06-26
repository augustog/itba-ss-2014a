import math
import random


STREETS = 5
ROAD_LENGTH = STREETS * 100
CHANCES_TO_ADD_AT_BEGINNING = 0.6

MIN_LANES_OCCUPIED = 3
MIN_CARS_PER_LANE = 4

def get_random_people_for_private_car():
    p = random.random()
    if p < 0.5:
        return 1
    elif p < 0.8:
        return 2
    elif p < 0.9:
        return 3
    else:
        return 4

def get_exit_road(position):
    p = random.random()
    if p < 0.6:
        return None
    return random.choice(range(
        math.ceil(position / 100 + 0.0001),
        ROAD_LENGTH / 100
    ))
