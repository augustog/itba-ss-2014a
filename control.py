import math
import random

import car as car_module

MPS_PER_METER = 3
DISTANCE_MARGIN = 1
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

def get_prev_car(car, lane):
    return _prev_in_set(car.position,
        filter(lambda x: x is not car, lane.cars), get_position)

def get_next_car(car, lane):
    return _next_in_set(car.position,
        filter(lambda x: x is not car, lane.cars), get_position)

def can_advance(car, lane, traffic_lights, time):
    pos = car.position
    next_car = get_next_car(car, lane)

    if is_first_on_traffic_light(car, lane, traffic_lights):
        next_traffic_light = get_next_traffic_light(car, traffic_lights)
        if not next_traffic_light:
            return True
        if next_traffic_light.is_green(time):
            return not next_car or rear(next_car, car.speed) > pos
        else:
            return next_traffic_light.position > pos
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

def advance(car, lane, traffic_lights, time, delta_time):
    next_car = get_next_car_before_next_traffic_light(
        car, lane, traffic_lights
    )
    if can_advance(car, lane, traffic_lights, time):
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
            # Traffic light ahead, or nothing
            next_traffic_light = get_next_traffic_light(car, traffic_lights)
            if not next_traffic_light:
                car.set_acceleration(car.max_acceleration, delta_time)
            else:
                target_time = get_target_time(car,
                    next_traffic_light.position - car.position
                )
                if target_time < 0.1 and next_traffic_light.is_green(time):
                    car.set_acceleration(car.max_acceleration, delta_time)
                else:
                    distance_to_traffic_light = (next_traffic_light.position
                        - car.position)
                    if distance_to_traffic_light > DISTANCE_MARGIN:
                        if next_traffic_light.is_green(time + target_time):
                            # Light will be green when we get there. Keep moving.
                            # TODO: Check if there will be a car after the traffic light
                            # that won't let this car cross it.
                            car.set_acceleration(car.max_acceleration, delta_time)
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

    car.advance(delta_time)
    if not next_car:
        next_traffic_light = get_next_traffic_light(car, traffic_lights)
        if next_traffic_light:
            if abs(car.position - next_traffic_light.position) < DISTANCE_MARGIN:
                if car.acceleration < 0:
                    car.position = next_traffic_light.position
                    car.speed = 0

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

def can_change_lane(car, to_lane, traffic_lights):
    next_car = get_next_car(car, to_lane)
    side_car = get_prev_car(next_car, to_lane)

def should_change_lane_to_move_faster(car, from_lane, target_lanes,
    traffic_lights):
    pass

def should_change_lane_to_turn(car, from_lane, lanes, traffic_lights):
    pass

car_lane = lambda y: lambda x: not x.exclusive and x.way == y

def make_cars_appear(lanes, sources, traffic_lights, time, delta_time):
    for source, light in zip(sources['car'], traffic_lights):
        for direction in ('NORTH', 'SOUTH'):
            src = source[direction]
            if not light.is_green(time):
                if src.chances_to_appear(delta_time):
                    # TODO: Calculate exit_road and people_carried
                    new_car = car_module.Car(
                        light.position + car_module.Car.length
                        + DISTANCE_MARGIN, 0, 0, 0
                    )
                    targets = filter(car_lane(direction), lanes)
                    targets = filter(
                        lambda x: not get_next_car(new_car, x) or
                            rear(get_next_car(new_car, x), 0)
                                > new_car.position + DISTANCE_MARGIN, targets
                    )
                    if targets:
                        random.choice(targets).add_car(new_car)
                        src.reset()
    for index, lane in enumerate(lanes):
        src = sources['lanes'][index]
        if src.chances_to_appear(delta_time):
            # TODO: Calculate exit_road and people_carried
            new_car = car_module.Car(0, 0, 0, 0)
            next_car = get_next_car(new_car, lane)
            if not next_car or (
                rear(next_car, 0) > new_car.position + DISTANCE_MARGIN):
                lane.add_car(new_car)
                src.reset()

def make_buses_appear(lanes, agenda, time, delta_time):
    pass

