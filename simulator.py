from config import *

import source
import control
import trafficlight
from car import Car
from control import *

def get_blocks_before_turn(new_car):
    if new_car.exit_road:
        return new_car.exit_road - int(new_car.position/100)
    return None

class Simulator(object):

    def __init__(self, lanes, lines):

        self.current_time = 0
        self.warmup_time = 0
        self.delta_t = 0.125
        self.last_300 = []
        self.last_300_private = []

        self.people_source = source.Source(1)
        self.car_source = source.Source(1)

        self.warmup = True
        self.init_target_functions()
        self.init_lanes(lanes)
        self.init_queues()
        self.init_elements(lines)

        self.listener = None

    def add_listener(self, listener):
        self.listener = listener

    def init_elements(self, lines):
        self.lights = []
        self.cars = []
        self.buses = []
        self.lines = lines
        for i in range(1, STREETS):
            self.lights.append(trafficlight.TrafficLight(i * 100, 30))

    def init_lanes(self, lanes):
        self.lanes = lanes
        self.bus_start_lane = lanes[0]
        exclusives = False
        prev = None
        for lane in lanes[0:]:
            exclusives = exclusives or lane.exclusive
            lane.prev = prev
            prev = lane
            if lane.exclusive or not exclusives:
                self.bus_start_lane = lane
        for lane in lanes[-2::-1]:
            lane.next = prev
            prev = lane
        for index, lane in enumerate(filter(lambda x: x.exclusive, lanes)):
            lane.index = index
        for index, lane in enumerate(filter(lambda x: not x.exclusive, lanes)):
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

    def init_queues(self):
        self.car_queues_init = [
            ([], lane) for lane in self.lanes if not lane.exclusive
        ]
        self.car_queues_corners = [
            ([], p) for p in range(100, ROAD_LENGTH, 100)
        ]
        self.bus_queue = []

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
        if self.listener:
            self.listener.pre_loop(self)
        self.advance_cars()

        # Ascenso y descenso de personas en buses
        for bus2 in self.buses:
            if bus2.just_stopped:
                number_left = bus2.people_leave()
                if not self.warmup:
                    self.people_finished_public += number_left
                self.people_in_the_system_public -= number_left
                number = bus2.closest_stop.bus_arrived(bus2)
                bus2.delay_time = DELAY_PER_PERSON * number
                bus2.people_carried += number
                bus2.just_stopped = False

        if self.bus_queue:
            new_car = self.bus_queue[0]
            if (not get_next_car(new_car, self.bus_start_lane)) \
                    or rear(get_next_car(new_car, self.bus_start_lane), 0) > DISTANCE_MARGIN:
                self.bus_start_lane.add_car(self.bus_queue.pop(0))

        for queue in self.car_queues_init:
            if len(queue[0]):
                lane = queue[1]
                new_car = queue[0][0]
                if (not get_next_car(new_car, lane)) \
                        or rear(get_next_car(new_car, lane), 0) > DISTANCE_MARGIN:
                    new_car.position += new_car.length + DISTANCE_MARGIN
                    lane.add_car(queue[0].pop(0))

        for queue in self.car_queues_corners:
            if len(queue[0]) and not self.lights[0].is_green(self.current_time):
                new_car = queue[0][0]
                target_lanes = filter(lambda x:
                        not x.exclusive and
                        (not get_next_car(new_car, x)
                            or rear(get_next_car(new_car, x), 0)
                                > new_car.position + DISTANCE_MARGIN),
                    self.lanes
                )
                if target_lanes:
                    new_car.position += new_car.length + DISTANCE_MARGIN
                    random.choice(target_lanes).add_car(queue[0].pop(0))

        if self.people_source.chances_to_appear(self.delta_t):
            line = random.choice(self.lines)
            stop = random.choice(line.bus_stops)
            stop.person_arrived()
            self.people_in_the_system_public += 1
            self.people_source.reset()

        # TEA para autos ingresando al sistema
        if self.car_source.chances_to_appear(self.delta_t):
            new_car = Car(0, 0, 0, 0, get_random_people_for_private_car())
            if random.random() < CHANCES_TO_ADD_AT_BEGINNING:
                random.choice(self.car_queues_init)[0].append(new_car)
            else:
                where = random.choice(self.car_queues_corners)
                where[0].append(new_car)
                new_car.position = where[1]
            self.cars.append(new_car)
            self.people_in_the_system_private += new_car.people_carried
            new_car.exit_road = get_exit_road(new_car.position)
            new_car.blocks_before_turn = get_blocks_before_turn(new_car)
            new_car.started = self.current_time
            self.car_source.reset()

        for line in self.lines:
            if self.current_time - line.last_time_appeared > line.frequency:
                new_bus = line.new_bus()
                self.people_in_the_system_public += new_bus.people_carried
                line.last_time_appeared = self.current_time
                self.bus_queue.append(new_bus)
                self.buses.append(new_bus)

        if not self.warmup:
            self.time_spent_public += self.delta_t * self.people_in_the_system_public
            self.time_spent_private += self.delta_t * self.people_in_the_system_private
            for car in self.cars:
                self.meters_covered_private += car.last_delta * car.people_carried
            for bus in self.buses:
                self.meters_covered_public += bus.last_delta * bus.people_carried
        else:
            self.warmup = not control.has_warmup_finished(self.lanes, MIN_LANES_OCCUPIED, MIN_CARS_PER_LANE)
            if not self.warmup:
                self.warmup_time = self.current_time

        for car in control.remove_old_cars(self.lanes, 0, ROAD_LENGTH):
            self.people_in_the_system_private -= car.people_carried
            self.cars.remove(car)
            if not self.warmup:
                self.people_finished_private += car.people_carried

        for bus2 in control.remove_old_buses(self.lanes, 0, ROAD_LENGTH):
            self.people_in_the_system_public -= bus2.people_carried
            self.buses.remove(bus2)
            if not self.warmup:
                self.people_finished_public += bus2.people_carried

        self.current_time += self.delta_t
        if not self.warmup and self.current_time - math.ceil(self.current_time) == 0:
            if self.time_spent_private > 0 and self.time_spent_public > 0:
                self.last_300.append(self.public_speed())
                self.last_300_private.append(self.private_speed())
                if len(self.last_300) > 300:
                    self.last_300.pop(0)
                    self.last_300_private.pop(0)

        if self.listener:
            self.listener.after_loop(self)

    def private_speed(self):
        return self.meters_covered_private / self.time_spent_private
    def public_speed(self):
        return self.meters_covered_public / self.time_spent_public
    def private_transported(self):
        return self.people_finished_private
    def public_transported(self):
        return self.people_finished_public

    def has_finished(self):
        if self.warmup or len(self.last_300) != 300:
            return False
        len_public = len(self.last_300)
        mean_public = sum(self.last_300) / len_public
        std_public = math.sqrt(sum((x-mean_public)**2 for x in self.last_300) / len_public)
        len_private = len(self.last_300_private)
        mean_private = sum(self.last_300_private) / len_private
        std_private = math.sqrt(sum((x-mean_private)**2 for x in self.last_300_private) / len_private)
        return (
                not self.warmup
                and len(self.last_300) == 300
                and std_public < 0.01 * mean_public
                and std_private < 0.01 * mean_private
        )
