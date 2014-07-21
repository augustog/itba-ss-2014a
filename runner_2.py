from __future__ import division

import math
import bus_line
import bus_stop
import lane
import simulator as sim_module

import scipy.stats as st

from config import *
from config_pygame import *

print 'Tiempo, warmup, velocidad autos, velocidad buses, transportadas auto, transportadas buses'

condition = False


class StatisticalSignificanceAchiever(object):

    def __init__(self, alpha, margin):
        self.values = []
        self.alpha = alpha
        self.margin = margin

    def add_value(self, value):
        self.values.append(value)

    def is_achieved(self):
        n = len(self.values)
        if n < 4:
            return False

        x_sum = 0
        x2_sum = 0
        for x in self.values:
            x_sum += x
            x2_sum += x*x
        average = x_sum / n
        variance = (x2_sum - (x_sum*x_sum)/n)/(n - 1)
        std = math.sqrt(variance)
        zeta = float(st.norm.ppf(1 - self.alpha/2))
        print 'n = %d, zeta = %f, std = %f, average = %f, needed_n = %f' % (
                n, zeta, std, average,
                math.pow(zeta * std / (self.margin * average), 2)
        )

        return n > math.pow(zeta * std / (self.margin * average), 2)

stats = [
    StatisticalSignificanceAchiever(0.05, 0.10),
    StatisticalSignificanceAchiever(0.05, 0.10),
    StatisticalSignificanceAchiever(0.05, 0.10),
    StatisticalSignificanceAchiever(0.05, 0.10),
]

def _update_histograms(old_histograms, current_histograms, lines):
    histograms = {}
    for line in lines:
        new_histogram = []
        old_histogram = old_histograms[line]
        current_histogram = current_histograms[line]
        for i in range(len(old_histogram)):
            new_histogram.append(old_histogram[i] + current_histogram[i])
        histograms[line] = new_histogram

    return histograms

histograms = None

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

while not condition:
    config_lanes = [
        lane.Lane(),
        lane.Lane(True),
        lane.Lane(),
        lane.Lane(),
    ]
    config_lanes[0].exclusive = True
    config_lanes[1].exclusive = True

    line_1.last_time_appeared = 0
    line_2.last_time_appeared = 0
    line_3.last_time_appeared = 0
    line_4.last_time_appeared = 0

    sim = sim_module.Simulator(config_lanes, config_lines)

    if not histograms:
        histograms = {}
        for line in config_lines:
            histograms[line] = sim.build_histogram()

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
    stats[0].add_value(round_results[2])
    stats[1].add_value(round_results[3])
    stats[2].add_value(round_results[4])
    stats[3].add_value(round_results[5])

    histograms = _update_histograms(histograms, sim.arrival_histograms, config_lines)

    condition = all(stat.is_achieved() for stat in stats)

    print '%0.2f, %0.2f, %0.4f, %0.4f, %d, %d' % round_results

    print histograms
