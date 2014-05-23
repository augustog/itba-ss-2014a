from __future__ import division

# Standard library
import math
import random
import sys

# Third party library
import pygame
import pygame.locals as pg

# First party
import car
import control
import lane
import source
import trafficlight


# Define constants
STRONG = 'Strong'
LIGHT = 'Light'
DOTTED = 'Dotted'

DOTTED_LENGTH = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

STREETS = 5
ROAD_LENGTH = STREETS * 100

SCREEN_WIDTH = 1200
START_MARGIN = 50
SCALE_METERS_TO_SCREEN = (SCREEN_WIDTH - 2 * START_MARGIN) / ROAD_LENGTH

TEXT_MARGIN = 10
TEXT_LINE_MARGIN = 5
STATS_HEIGHT = 150
CAR_WIDTH = car.Car.length / 2 * SCALE_METERS_TO_SCREEN
CAR_HEIGHT = car.Car.length * SCALE_METERS_TO_SCREEN

LANE_WIDTH = 25
CAR_MARGIN = (LANE_WIDTH - CAR_HEIGHT) / 2
TRAFFIC_LIGHT_RADIUS = 10
TRAFFIC_LIGHT_MARGIN = 20
DOTTED_WIDTH = 2

# Setup the Simulation

current_time = 0
delta_t = 0.05

people_in_private_cars = 0
people_in_public_bus = 0

hours_spent_private_cars = 0
hours_spend_public_bus = 0

cars_finished_moving = 0
people_finished_moving_private = 0
people_finished_moving_public = 0

lanes = [
    lane.Lane('SOUTH'),
    lane.Lane('SOUTH'),
    lane.Lane('SOUTH'),
    lane.Lane('SOUTH'),
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

sources = {
    'car': [
        {
            'NORTH': source.Source(2),
            'SOUTH': source.Source(2)
        }
        for i in range(1, STREETS)
    ],
    'lanes': [
        source.Source(3)
        for i in range(len(lanes))
    ]
}

# Initialize

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, 400))

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
        hours_spent_private_cars, hours_spend_public_bus
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    if people_in_private_cars > 0 and people_in_public_bus > 0:
        time_text = font.render('Average time spent in traffic: %.2f, '
            'Average on buses: %.2f, Average on cars: %.2f' % (
            (hours_spend_public_bus + hours_spent_private_cars) /
            (people_finished_moving_private + people_finished_moving_public
                + people_in_public_bus + people_in_private_cars),
            (hours_spent_private_cars /
                (people_in_private_cars + people_finished_moving_private)),
            (hours_spend_public_bus /
                (people_in_public_bus + people_finished_moving_public)),
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
        if first or lanes[i].way != lanes[i-1].way:
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
    return RED

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
            draw_car(car, direction, lane_number)
        lane_number += 1

def advance_cars(current_time, lanes):
    for lane in lanes:
        for car in lane.cars:
            control.do_time_step(car, lane, lanes, 4, 4,
                lights, current_time, delta_t)
    return current_time + delta_t

def get_random_people_for_private_car():
    p = random.random()
    if p < 0.5:
        return 1
    if p < 0.8:
        return 2
    return math.ceil((p - 0.8) * 4) + 2

def get_exit_road(car):
    p = random.random()
    if p > 0.5:
        return None
    exit = math.ceil(p * 5)
    if exit * 100 > car.position:
        return exit
    return None

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
    for car in new_cars:
        car.people_carried += get_random_people_for_private_car()
        people_in_private_cars += car.people_carried
        car.exit_road = get_exit_road(car)
        cars.append(car)

    for car in control.remove_old_cars(lanes, 0, ROAD_LENGTH):
        people_in_private_cars -= car.people_carried
        cars.remove(car)
        cars_finished_moving += 1
        people_finished_moving_private += car.people_carried

    hours_spend_public_bus += delta_t * people_in_public_bus
    hours_spent_private_cars += delta_t * people_in_private_cars

    pygame.display.update()

