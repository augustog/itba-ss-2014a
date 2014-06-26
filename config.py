import math
import random

import bus_line
import bus_stop
import lane


STREETS = 5
BLOCK_LENGTH = 100
ROAD_LENGTH = STREETS * 100
CHANCES_TO_ADD_AT_BEGINNING = 0.6

MIN_LANES_OCCUPIED = 3
MIN_CARS_PER_LANE = 4

config_lanes = [
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
]

line_1 = bus_line.BusLine([
    bus_stop.BusStop(40),
    bus_stop.BusStop(240),
    bus_stop.BusStop(440),
], 1)

line_2 = bus_line.BusLine([
    bus_stop.BusStop(140),
    bus_stop.BusStop(340),
], 2)

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
    if int(math.ceil(position / 100 + 0.0001)) == STREETS:
        return None
    return random.choice(range(
        int(math.ceil(position / 100 + 0.0001)),
        STREETS
    ))
