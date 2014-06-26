import math
import random
from collections import defaultdict

from config import *

import bus as bus_module
import car as car_module
import bus_line
import bus_stop as bus_stop_module

MPS_PER_METER = 3.0
DISTANCE_MARGIN = 1
BUS_STOP_MARGIN = 5
BUS_STOP_DISTANCE = 1
MARGINAL_DISTANCE = 0.01

def _consecutive_in_set(value, elements, key, compare, select):
    candidates = filter(lambda x: compare(key(x), value), elements)
    return None if not len(candidates) else select(candidates, key=key)

def _prev_in_set(value, elements, key):
    return _consecutive_in_set(value, elements, key, lambda x, y: x <= y, max)

def _next_in_set(value, elements, key):
    return _consecutive_in_set(value, elements, key, lambda x, y: x >= y, min)

def rear(car, observer_speed):
    margin = math.ceil(observer_speed / MPS_PER_METER) or DISTANCE_MARGIN
    return car.position - car.length - margin

get_position = lambda x: x.position

def get_next_traffic_light(car, traffic_lights):
    return _next_in_set(car.position, traffic_lights, get_position)

def get_next_bus_stop(bus):
    return _next_in_set(bus.position, bus.line.bus_stops, get_position)

def get_prev_car(car, lane):
    return _prev_in_set(car.position,
        filter(lambda x: x is not car, lane.cars), get_position)

def get_next_car(car, lane):
    return _next_in_set(car.position,
        filter(lambda x: x is not car, lane.cars), get_position)

def can_advance(car, lane, lanes, traffic_lights, time):
    pos = car.position
    next_car = get_next_car(car, lane)
    lane_index = lanes.index(lane)

    if is_first_on_traffic_light(car, lane, traffic_lights):
        next_traffic_light = get_next_traffic_light(car, traffic_lights)
        if not next_traffic_light:
            return True
        if next_traffic_light.is_green(time):
            return not next_car or rear(next_car, car.speed) > pos
        else:
            return next_traffic_light.position > pos
    elif should_change_lane_to_turn(car, 100) and 0 < lane_index < len(lanes) - 1 and car.distance_to_target_position() <= 50:
        if can_change_lane(car, lane, _get_turning_lane(lane, lanes), traffic_lights):
            return True
        return False
    else:
        if not next_car:
            return True
        return rear(next_car, car.speed) > pos

def is_first_on_traffic_light(car, lane, traffic_lights):
    if get_next_car_before_next_traffic_light(car, lane, traffic_lights):
        return False
    return True

def get_next_car_before_next_traffic_light(car, lane, traffic_lights):
    next_traffic_light = get_next_traffic_light(car, traffic_lights)
    next_car = get_next_car(car, lane)
    if not next_car:
        return None
    else:
        if not next_traffic_light:
            return next_car
        if next_car.position <= next_traffic_light.position:
            return next_car
        return None

def advance(car, lane, lanes, traffic_lights, time, delta_time):
    next_car = get_next_car_before_next_traffic_light(
        car, lane, traffic_lights
    )
    if can_advance(car, lane, lanes, traffic_lights, time):
        if next_car:
            car_rear = rear(next_car, car.speed)
            car_distance = car_rear - car.position
            if car_distance < DISTANCE_MARGIN:
                car.speed = 0
                car.acceleration = 0
            else:
                accelerate_car_to_reach(car, next_car.speed,
                    max(0, car_distance - DISTANCE_MARGIN),
                    delta_time
                )
        elif should_change_lane_to_turn(car, 100) and 0 < lanes.index(lane) < len(lanes) - 1:
            # Has to stop.
            accelerate_car_to_reach(car, 0, car.distance_to_target_position() - 50, delta_time)
        else:
            # Traffic light ahead, or nothing
            next_traffic_light = get_next_traffic_light(car, traffic_lights)
            if not next_traffic_light:
                car.set_acceleration(car.max_acceleration, delta_time)
            else:
                if next_traffic_light.is_green(time):
                    if next_car:
                        car_rear = rear(next_car, car.speed)
                        car_distance = car_rear - car.position
                        if car_distance < DISTANCE_MARGIN:
                            car.speed = 0
                            car.acceleration = 0
                        else:
                            accelerate_car_to_reach(car, next_car.speed,
                                max(0, car_distance - DISTANCE_MARGIN),
                                delta_time
                            )
                    else:
                        car.set_acceleration(car.max_acceleration, delta_time)
                else:
                    target_time = get_target_time(car,
                        next_traffic_light.position - car.position
                    )
                    distance_to_traffic_light = (next_traffic_light.position
                        - car.position)
                    if distance_to_traffic_light > DISTANCE_MARGIN:
                        if next_traffic_light.is_green(time + target_time):
                            if next_car:
                                car_rear = rear(next_car, car.speed)
                                car_distance = car_rear - car.position
                                if car_distance < DISTANCE_MARGIN:
                                    car.speed = 0
                                    car.acceleration = 0
                                else:
                                    accelerate_car_to_reach(car, next_car.speed,
                                        max(0, car_distance - DISTANCE_MARGIN),
                                        delta_time
                                    )
                            else:
                                car.set_acceleration(car.max_acceleration,
                                        delta_time)
                        else:
                            accelerate_car_to_reach(car, 0,
                                max(0, distance_to_traffic_light - DISTANCE_MARGIN),
                                delta_time
                            )
                    else:
                        car.speed = 0
                        car.acceleration = 0
    else:
        car.speed = 0
        car.acceleration = 0

    if (isinstance(car, bus_module.Bus) and
            can_advance(car, lane, lanes, traffic_lights, time)):
        next_stop = get_next_bus_stop(car)
        if next_stop:
            distance = next_stop.position - car.position
            if distance < BUS_STOP_DISTANCE:
                car.just_stopped = True
                car.closest_stop = next_stop
            elif distance < BUS_STOP_MARGIN:
                accelerate_car_to_reach(car, 0, distance, delta_time)

    car.advance(delta_time)

def accelerate_car_to_reach(car, target_speed, distance, delta_time):
    acceleration_to_reach = car.acceleration_to_reach(0,
            distance, delta_time)
    if abs(acceleration_to_reach) > car.max_acceleration:
        car.set_acceleration(acceleration_to_reach, delta_time)
    else:
        car.set_acceleration(car.max_acceleration, delta_time)

# Solves the time vs position function and returns the lowest positive value.
# This function assumes that there will always be a positive solution.
def solve_quadratic_equation(a, b, c):
    discriminant = math.sqrt(math.pow(b, 2) - 4 * a * c)
    solution1 = (-b + discriminant) / 2 / a
    solution2 = (-b - discriminant) / 2 / a
    if solution1 < 0:
        return solution2
    if solution2 < 0:
        return solution1
    return min(solution1, solution2)

def solve_car_time_equation(car, distance):
    return solve_quadratic_equation(1.0 / 2 * car.max_acceleration,
        car.speed, -distance
    )

def get_target_time(car, distance):
    distance_to_max_speed = ((math.pow(car.max_speed, 2) -
        math.pow(car.speed, 2)) / (2 * car.max_acceleration)
    )
    if distance_to_max_speed > distance:
        target_time = solve_car_time_equation(car, distance)
    else:
        accelerating_time = solve_car_time_equation(car, distance_to_max_speed)
        target_time = ((distance - distance_to_max_speed)
            / car.max_speed + accelerating_time)
    return target_time

def _get_target_lanes(lane, lanes):
    return [lane.prev, lane.next]

def do_time_step(car, lane, lanes, traffic_lights, current_time, delta_t):
    target_lane = decide_lane_change(car, lane, lanes, traffic_lights, current_time, delta_t)
    if target_lane:
        change_lane(car, lane, target_lane)
    else:
        advance(car, lane, lanes, traffic_lights, current_time, delta_t)

def _get_turning_lane(lane, lanes):
    lane_index = lanes.index(lane)
    return lanes[lane_index + 1]

def decide_lane_change(car, lane, lanes, traffic_lights, current_time, delta_t):
    target_faster = should_change_lane_to_move_faster(car, lane,
                    _get_target_lanes(lane, lanes), traffic_lights)
    lane_index = lanes.index(lane)
    target_turning = None
    if lane_index != 0 and lane_index != len(lanes) - 1 and should_change_lane_to_turn(car, lane_index):
        target_turning = _get_turning_lane(lane, lanes)
    if target_faster or target_turning:
        if car.change_lane.chances_to_appear(delta_t):
            if target_turning:
                if can_change_lane(car, lane, target_turning, traffic_lights):
                    car.change_lane.reset()
                    return target_turning
                else:
                    return None
            if not target_turning and not should_change_lane_to_turn(car, lane_index) and target_faster and can_change_lane(car, lane, target_faster, traffic_lights):
                car.change_lane.reset()
                return target_faster

def should_change_lane_to_turn(car, block_length):
    return (car.exit_road and
        car.position >= (car.exit_road - car.blocks_before_turn) * block_length)

def change_lane(car, from_lane, to_lane):
    from_lane.remove_car(car)
    to_lane.add_car(car)

def can_change_lane(car, current_lane, to_lane, traffic_lights):
    next_car = get_next_car(car, to_lane)
    side_car = get_prev_car(car, to_lane)
    next_traffic_light = get_next_traffic_light(car, traffic_lights)
    if (current_lane.exclusive != to_lane.exclusive or
           (side_car and side_car.position >= rear(car, side_car.speed)) or
           (next_car and car.position >= rear(next_car, car.speed)) or
           (next_traffic_light and
           next_traffic_light.position - car.position < car.length * 1.5)):
        # If the car changes lanes the car behind it will be too close
        # or it will be too close to the next car.
        # If the car is too close to the traffic light then it won't
        # change lane either.
        return False
    return True

# target_lanes should be an array with exactly 2 lanes.
def should_change_lane_to_move_faster(car, from_lane, target_lanes, traffic_lights):
    next_pos0 = False
    next_pos1 = False
    next_pos_current = False
    to_lane0 = None
    to_lane1 = None
    if target_lanes[0]:
        to_lane0 = can_change_lane(car, from_lane, target_lanes[0], traffic_lights)
        next_car = get_next_car(car, target_lanes[0])
        if next_car:
            next_pos0 = next_car.position
    if target_lanes[1]:
        to_lane1 = can_change_lane(car, from_lane, target_lanes[1], traffic_lights)
        next_car = get_next_car(car, target_lanes[1])
        if next_car:
            next_pos1 = next_car.position
    next_car = get_next_car(car, from_lane)
    if next_car:
        next_pos_current = next_car.position
    if not next_pos_current:
        return False
    if to_lane0 and to_lane1:
        # Car can go to both lanes. Check which lane is better.
        if not next_pos0:
            return target_lanes[0]
        if not next_pos1:
            return target_lanes[1]
        if next_pos_current > next_pos0 and next_pos_current > next_pos1:
            return False
        if next_pos0 > next_pos1:
            return target_lanes[0]
        return target_lanes[1]
    if to_lane0:
        if next_pos_current > next_pos0:
            return False
        return target_lanes[0]
    if to_lane1:
        if next_pos_current > next_pos1:
            return False
        return target_lanes[1]
    return False

def bus_stop(bus, stop):
    bus.pick_up_people(stop.bus_arrived(bus))

car_lane = lambda x: not x.exclusive

def make_cars_appear(lanes, sources, traffic_lights, time, delta_time):
    new_cars = []
    for source, light in zip(sources['car'], traffic_lights):
        for direction in ('NORTH', 'SOUTH'):
            src = source[direction]
            if not light.is_green(time):
                if src.chances_to_appear(delta_time):
                    new_car = car_module.Car(
                        light.position + car_module.Car.length
                        + DISTANCE_MARGIN, 0, 0, 0, 0
                    )
                    targets = filter(car_lane, lanes)
                    targets = filter(
                        lambda x: not get_next_car(new_car, x) or
                            rear(get_next_car(new_car, x), 0)
                                > new_car.position + DISTANCE_MARGIN, targets
                    )
                    if targets:
                        new_cars.append(new_car)
                        random.choice(targets).add_car(new_car)
                        src.reset()
    for index, lane in enumerate(lanes):
        src = sources['lanes'][index]
        if not lane.exclusive and src.chances_to_appear(delta_time):
            new_car = car_module.Car(0, 0, 0, 0, 0)
            next_car = get_next_car(new_car, lane)
            if not next_car or (
                rear(next_car, 0) > new_car.position + DISTANCE_MARGIN):
                lane.add_car(new_car)
                new_cars.append(new_car)
                src.reset()
    return new_cars

def make_buses_appear(lanes, sources, time, delta_time):
    new_buses = []
    for index, bus_sources in enumerate(sources['bus']):
        if bus_sources:
            for x in bus_sources:
                line = x['line']
                source = x['source']
                if source and source.chances_to_appear(delta_time):
                    new_bus = bus_module.Bus(line, 0, 0)
                    next_car = get_next_car(new_bus, lanes[index])
                    if not next_car or (
                            rear(next_car, 0) > new_bus.position + DISTANCE_MARGIN):
                        lanes[index].add_car(new_bus)
                        new_buses.append(new_bus)
                        source.reset()
    return new_buses

def remove_old_vehicles(lanes, start, end, vehicleType):
    removed = []
    for lane in lanes:
        for vehicle in lane.cars:
            if start > vehicle.position or end < vehicle.position:
                if vehicle.__class__.__name__ == vehicleType:
                    removed.append(vehicle)
                    lane.remove_car(vehicle)
            elif vehicleType == 'Car' and vehicle.__class__.__name__ == 'Car':
                if vehicle.exit_road and vehicle.position > vehicle.exit_road * 100:
                    removed.append(vehicle)
                    lane.remove_car(vehicle)
    return removed

def remove_old_cars(lanes, start, end):
    return remove_old_vehicles(lanes, start, end, 'Car')

def remove_old_buses(lanes, start, end):
    return remove_old_vehicles(lanes, start, end, 'Bus')

def has_warmup_finished(lanes, min_lanes, min_cars):
    cars_per_block = defaultdict(int)
    for lane in lanes:
        for car in lane.cars:
            cars_per_block[str(math.ceil(car.position/100))] += 1
    if sum([1 if block_cars > min_cars else 0 for block_cars in cars_per_block.values()]) > min_lanes:
        return True
    return False

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
