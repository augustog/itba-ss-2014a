import math
import random

import bus_line
import bus_stop
import lane


STREETS = 5
BLOCK_LENGTH = 100
ROAD_LENGTH = STREETS * 100
CHANCES_TO_ADD_AT_BEGINNING = 0.6

MIN_LANES_OCCUPIED = 4
MIN_CARS_PER_LANE = 10

config_lanes = [
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
]
config_lanes[0].exclusive = True

line_1 = bus_line.BusLine([
    bus_stop.BusStop(i) for i in range(40, ROAD_LENGTH, 200)
], 70)

line_2 = bus_line.BusLine([
    bus_stop.BusStop(i) for i in range(140, ROAD_LENGTH, 200)
], 120)

line_3 = bus_line.BusLine([
    bus_stop.BusStop(i) for i in range(80, ROAD_LENGTH, 200)
], 110)

line_4 = bus_line.BusLine([
    bus_stop.BusStop(i) for i in range(180, ROAD_LENGTH, 200)
], 230)

config_lines = [line_1, line_2, line_3, line_4]

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

