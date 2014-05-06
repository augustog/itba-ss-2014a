import math

MPS_PER_METER = 3

def _next_in_set(value, elements, key):
    next_elements = filter(lambda x: key(x) >= value, elements)
    return min(next_elements, key=key)

def rear(car, observer_speed):
    margin = math.ceil(observer_speed / MPS_PER_METER) or 1
    return car.pos - car.length - margin

def can_advance(car, lane, semaphores, time):
    pos = car.position
    get_position = lambda x: x.position

    next_car = _next_in_set(
            pos, filter(lambda x: x is not car, lane.cars), get_position
    )

    if car.halted_on_light:
        next_semaphore = _next_in_set(pos, semaphores, get_position)
        return next_semaphore.is_green(time) \
                and not next_car or rear(next_car, car.speed) > pos
    else:
        return not next_car or rear(next_car, car.speed) > pos

