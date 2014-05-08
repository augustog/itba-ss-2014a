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
            acceleration = get_target_acceleration(car, next_car)
            car.speed = car.speed + acceleration * delta_time
        car.advance(delta_time)

    else: # Traffic light ahead
        pass

def get_target_acceleration(car, next_car):
    return -math.pow(next_car.speed - car.speed, 2) / (
            2 * (next_car.position - car.position + DISTANCE_MARGIN)

