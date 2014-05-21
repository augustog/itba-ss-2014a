from __future__ import division

# Standard library
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
FIELD_LENGTH = STREETS * 100

SCREEN_WIDTH = 1200
START_MARGIN = 50
SCALE_METERS_TO_SCREEN = (SCREEN_WIDTH - 2 * START_MARGIN) / FIELD_LENGTH

TEXT_MARGIN = 10
STATS_HEIGHT = 100
CAR_WIDTH = car.Car.length / 2 * SCALE_METERS_TO_SCREEN
CAR_HEIGHT = car.Car.length * SCALE_METERS_TO_SCREEN

LANE_WIDTH = 25
CAR_MARGIN = (LANE_WIDTH - CAR_HEIGHT) / 2
TRAFFIC_LIGHT_RADIUS = 10
TRAFFIC_LIGHT_MARGIN = 20
DOTTED_WIDTH = 2

# Setup the Simulation

current_time = 0
delta_t = 0.1

lanes = [
    lane.Lane('SOUTH'),
    lane.Lane('SOUTH'),
    lane.Lane(),
    lane.Lane(),
    lane.Lane(),
]

lights = []
cars = []

for i in range(1, STREETS):
    lights.append(trafficlight.TrafficLight(i * 100, 5))

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
    time_text = font.render('Time: %.2f' % current_time, True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, TEXT_MARGIN))

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
            control.advance(car, lane, lights, current_time, delta_t)
    return current_time + delta_t

trafficlight.TrafficLight.period_in_secs = 3

while True:
    for event in pygame.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    screen.fill(WHITE)
    current_time = advance_cars(current_time, lanes)
    draw_data()
    draw_lanes(lanes)
    draw_cars(lanes)
    control.make_cars_appear(lanes, sources, lights, current_time, delta_t)

    pygame.display.update()

