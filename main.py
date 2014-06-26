from __future__ import division

# Standard library
import math
import random
import sys

# Third party library
import pygame
import pygame.locals as pg

# First party
import bus
import bus_line
import bus_stop
import car
import control
import lane
import source
import trafficlight

from config import *


# Initialize

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def draw_line(line_type=STRONG, from_x=0, to_x=0, y=0, color=BLACK):
    if line_type == DOTTED:
        draw_dotted_line(from_x, to_x, y, color)
    else:
        width = 4 if line_type == STRONG else DOTTED_WIDTH
        pygame.draw.line(screen, color, (from_x, y), (to_x, y), width)

def draw_dotted_line(from_x, to_x, y, color):
    for i in range(from_x, to_x, DOTTED_LENGTH):
        pygame.draw.line(
            screen, color, (i, y), (i + DOTTED_LENGTH / 2, y), DOTTED_WIDTH
        )

font = pygame.font.Font(None, 24)

def draw_data():
    y = TEXT_MARGIN
    time_text = font.render('Time: %.2f' % current_time, True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('Cars: %d, Buses: %d' % (
        len(cars), len(buses)
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('People on cars: %d, People on buses: %d' % (
        people_in_private_cars, people_in_public_bus
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('People that finished traveling in cars: %d'
        ', in bus: %d, total: %d' % (
        people_finished_moving_private,
        people_finished_moving_public,
        people_finished_moving_public + people_finished_moving_private
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('Hours on cars: %d, Hours on buses: %d' % (
        hours_total_private_cars, hours_total_public_bus
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    if people_finished_moving_private > 0:
        time_text = font.render('Average time spent in traffic: %.2f, '
            'Average on buses: %.2f, Average on cars: %.2f' % (
            (hours_spent_public_bus + hours_spent_private_cars) /
            (people_finished_moving_private + people_finished_moving_public),
            (hours_spent_public_bus / people_finished_moving_public) if people_finished_moving_public else 0,
            (hours_spent_private_cars / people_finished_moving_private),
        ), True, BLACK)
        screen.blit(time_text, (TEXT_MARGIN, y))
        y += time_text.get_height() + TEXT_LINE_MARGIN


def draw_lanes(lanes):
    first = True
    y = STATS_HEIGHT
    start = START_MARGIN
    end = SCREEN_WIDTH - START_MARGIN
    for i in range(0, len(lanes)):
        line_type = DOTTED
        if first or lanes[i].way != lanes[i-1].way \
                or lanes[i].exclusive != lanes[i-1].exclusive:
            line_type = STRONG
        draw_line(line_type, start, end, y)
        y += LANE_WIDTH
        first = False
    draw_line(STRONG, start, end, y)
    for light in lights:
        pygame.draw.circle(screen,
            GREEN if light.is_green(current_time) else RED,
            (
                int(START_MARGIN + light.position * SCALE_METERS_TO_SCREEN),
                int(y + TRAFFIC_LIGHT_MARGIN)
            ),
            TRAFFIC_LIGHT_RADIUS
        )


def get_color(car):
    if (control.should_change_lane_to_turn(car, BLOCK_LENGTH)):
        return GREEN
    return RED

def draw_bus(bus, direction, lane_number):
    start = START_MARGIN if direction == 1 else SCREEN_WIDTH - START_MARGIN
    pygame.draw.rect(
        screen, YELLOW,
        pygame.Rect(
            start + bus.position * SCALE_METERS_TO_SCREEN * direction,
            STATS_HEIGHT + LANE_WIDTH * lane_number + BUS_MARGIN,
            BUS_HEIGHT * -1 * direction,
            BUS_WIDTH
        )
    )

def draw_car(car, direction, lane_number):
    start = START_MARGIN if direction == 1 else SCREEN_WIDTH - START_MARGIN
    pygame.draw.rect(
        screen, get_color(car),
        pygame.Rect(
            start + car.position * SCALE_METERS_TO_SCREEN * direction,
            STATS_HEIGHT + LANE_WIDTH * lane_number + CAR_MARGIN,
            CAR_HEIGHT * -1 * direction,
            CAR_WIDTH
        )
    )

def draw_cars(lanes):
    lane_number = 0
    for lane in lanes:
        direction = 1 if lane.way == 'NORTH' else -1
        for car in lane.cars:
            if isinstance(car, bus.Bus):
                draw_bus(car, direction, lane_number)
            else:
                draw_car(car, direction, lane_number)
        lane_number += 1


def get_blocks_before_turn():
    p = random.random()
    if p < 0.6:
        return 1
    elif p < 0.9:
        return 2
    else:
        return 3

warmup = True

while True:
    for event in pygame.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    screen.fill(WHITE)
    current_time = advance_cars(current_time, lanes)
    draw_data()
    draw_lanes(lanes)
    draw_cars(lanes)
    new_cars = control.make_cars_appear(
        lanes, sources, lights, current_time, delta_t
    )
    new_buses = control.make_buses_appear(
        lanes, sources, current_time, delta_t
    )
    for car in new_cars:
        car.people_carried += get_random_people_for_private_car()
        people_in_private_cars += car.people_carried
        car.exit_road = get_exit_road(car)
	car.blocks_before_turn = get_blocks_before_turn();
        car.started = current_time
        cars.append(car)

    for bus2 in new_buses:
        bus2.people_carried += get_random_people_for_public_bus()
        people_in_public_bus += bus2.people_carried
        bus2.started = current_time
        buses.append(bus2)

    for car in control.remove_old_cars(lanes, 0, ROAD_LENGTH):
        people_in_private_cars -= car.people_carried
        cars.remove(car)
        # Not used.
        cars_finished_moving += 1
	if not warmup:
    	    people_finished_moving_private += car.people_carried
	    hours_spent_private_cars += (current_time - car.start_time)

    for bus2 in control.remove_old_buses(lanes, 0, ROAD_LENGTH):
        people_in_public_bus -= bus2.people_carried
        buses.remove(bus2)
        if not warmup:
            people_finished_moving_public += bus2.people_carried
            hours_spent_public_bus += (current_time - bus2.start_time)

    if not warmup:
        hours_total_public_bus += delta_t * people_in_public_bus
        hours_total_private_cars += delta_t * people_in_private_cars
    else:
        warmup = control.has_warmup_finished(lanes, MIN_LANES_OCCUPIED,
            MIN_CARS_PER_LANE)

    pygame.display.update()

