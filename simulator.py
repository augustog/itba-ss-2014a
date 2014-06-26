from config import *


class Simulator(object):

    def __init__(self, lanes, listener):

        self.current_time = 0
        self.delta_t = 0

        self.warmup = True
        self.init_target_functions()
        self.init_lanes(lanes)

        self.listener = listener
        listener.init()

    def init_lanes(self, lanes):
        self.lanes = lanes
        prev = lanes[0]
        for lane in lanes[1:]:
            lane.prev = prev
            prev = lane
        for lane in lanes[-2::-1]:
            lane.next = prev
            prev = lane
        for index, lane in enumerate(filter(lanes, lambda x: x.exclusive)):
            lane.index = index
        for index, lane in enumerate(filter(lanes, lambda x: not x.exclusive)):
            lane.index = index

    def init_target_functions(self):

        self.meters_covered_public = 0
        self.meters_covered_private = 0

        self.time_spent_public = 0
        self.time_spent_private = 0

        self.people_finished_public = 0
        self.people_finished_private = 0

        self.people_in_the_system_public = 0
        self.people_in_the_system_private = 0

    def advance_cars(self):
        for lane in self.lanes:
            for car in lane.cars:
                control.do_time_step(
                    car,
                    lane,
                    self.lanes,
                    self.lights,
                    self.current_time,
                    self.delta_t
                )
        self.current_time += self.delta_t

    def loop(self):
        self.listener.prev_loop(self)
        self.advance_cars()


lanes = [
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
]

lights = []
cars = []
buses = []

for i in range(1, STREETS):
    lights.append(trafficlight.TrafficLight(i * 100, 30))

line_152_1 = bus_line.BusLine([
    bus_stop.BusStop(lanes[3], 40, 0),
    bus_stop.BusStop(lanes[3], 240, 0),
    bus_stop.BusStop(lanes[3], 440, 0),
], 0, ROAD_LENGTH)

line_152_2 = bus_line.BusLine([
    bus_stop.BusStop(lanes[6], 140, 0),
    bus_stop.BusStop(lanes[6], 340, 0),
], 0, ROAD_LENGTH)

sources = {
    'car': [
        {
            'NORTH': source.Source(6),
            'SOUTH': source.Source(6)
        }
        for i in range(1, STREETS)
    ],
    'lanes': [
        source.Source(9)
        for i in range(len(lanes))
    ],
    'bus': [ None for i in range(len(lanes)) ]
}
sources['bus'][3] = [{'source': source.Source(20), 'line': line_152_1}]
sources['bus'][4] = [{'source': source.Source(20), 'line': line_152_2}]
