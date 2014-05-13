import math
import car as car_module

MPS_PER_METER = 3
DISTANCE_MARGIN = 1

def _next_in_set(value, elements, key):
    next_elements = filter(lambda x: key(x) >= value, elements)
    return None if not len(next_elements) else min(next_elements, key=key)

def rear(car, observer_speed):
    margin = math.ceil(observer_speed / MPS_PER_METER) or DISTANCE_MARGIN
    return car.position - car.length - margin

get_position = lambda x: x.position

def get_next_traffic_light(car, traffic_lights):
    return _next_in_set(car.position, traffic_lights, get_position)

def get_next_car(car, lane):
    return _next_in_set(car.position, filter(lambda x: x is not car, lane.cars), get_position)

def can_advance(car, lane, traffic_lights, time):
    pos = car.position
    next_car = get_next_car(car, lane)

    if car.is_first_on_traffic_light():
        next_traffic_light = get_next_traffic_light(car, traffic_lights)
        return next_traffic_light.is_green(time) \
                and (not next_car or rear(next_car, car.speed) > pos)
    else:
        return not next_car or rear(next_car, car.speed) > pos

def get_next_car_before_next_traffic_light(car, lane, traffic_lights):
    next_traffic_light = get_next_traffic_light(car, traffic_lights)
    next_car = get_next_car(car, lane)

    return next_car and ((not next_traffic_light and next_car) or
        (next_car.position < next_traffic_light.position and next_car))

def advance(car, lane, traffic_lights, time, delta_time):
    next_car = get_next_car_before_next_traffic_light(
        car, lane, traffic_lights
    )
    if next_car:
        if can_advance(car, lane, traffic_lights, time):
            car.accelerate(delta_time)
        else:
            car.set_speed(next_car.speed, next_car.position - DISTANCE_MARGIN)
    else: # Traffic light ahead
        next_traffic_light = get_next_traffic_light(car, traffic_lights)
        target_time = get_target_time(car,
            next_traffic_light.position - car.position
        )
        if next_traffic_light.is_green(target_time):
            # Light will be green when we get there. Keep moving.
            # TODO: Check if there will be a car after the traffic light that
            # won't let this car cross it.
            car.accelerate(delta_time)
        else:
            distance_to_traffic_light = (car.position / 100 + 1) * 100 - car.position
            car.set_speed(0, distance_to_traffic_light)
    car.advance(delta_time)

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
    return solve_quadratic_equation(1.0 / 2 * car.acceleration,
        car.speed, -distance
    )

def get_target_time(car, distance):
    distance_to_max_speed = ((math.pow(car.max_speed, 2) -
        math.pow(car.speed, 2)) / (2 * car.acceleration)
    )
    if distance_to_max_speed > distance:
	target_time = solve_car_time_equation(car, distance)
    else:
        accelerating_time = solve_car_time_equation(car, distance_to_max_speed)
        target_time = (distance - distance_to_max_speed) / car.max_speed + accelerating_time
    return target_time

