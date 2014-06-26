from __future__ import division

# Standard library
import math
import random
import sys

# First party
import bus
import bus_line
import bus_stop
import car
import control
import lane
import simulator as sim_module
import source
import trafficlight

from config import *
from config_pygame import *

print 'Tiempo, warmup, velocidad autos, velocidad buses, transportadas auto, transportadas buses'

condition = False

while not condition:
    config_lanes = [
        lane.Lane(),
        lane.Lane(),
        lane.Lane(),
        lane.Lane(),
    ]
    config_lanes[0].exclusive = True

    line_1 = bus_line.BusLine([
        bus_stop.BusStop(40),
        bus_stop.BusStop(240),
        bus_stop.BusStop(440),
    ], 70)

    line_2 = bus_line.BusLine([
        bus_stop.BusStop(140),
        bus_stop.BusStop(340),
    ], 120)

    line_3 = bus_line.BusLine([
        bus_stop.BusStop(80),
        bus_stop.BusStop(280),
        bus_stop.BusStop(480),
    ], 110)

    line_4 = bus_line.BusLine([
        bus_stop.BusStop(180),
        bus_stop.BusStop(380),
    ], 230)

    config_lines = [line_1, line_2, line_3, line_4]
    sim = sim_module.Simulator(config_lanes, config_lines)

    while not sim.has_finished():
        sim.loop()

    round_results = (
        sim.current_time,
        sim.warmup_time,
        sim.private_speed(),
        sim.public_speed(),
        sim.private_transported(),
        sim.public_transported()
    )

    print '%0.2f, %0.2f, %0.4f, %0.4f, %d, %d' % round_results
