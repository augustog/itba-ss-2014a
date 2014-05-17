# Standard library
import sys

# Third party library
import pygame
import pygame.locals as pg

# First party
import car
import control
import lane
import trafficlight


# Define constants
STRONG = 'Strong'
LIGHT = 'Light'
DOTTED = 'Dotted'

DOTTED_LENGTH = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

SCREEN_WIDTH = 1200
START_MARGIN = 50
STATS_HEIGHT = 100
CAR_WIDTH = 25
CAR_HEIGHT = 40
LANE_WIDTH = 40
CAR_MARGIN = 9
SCALE_METERS_TO_SCREEN = 10
DOTTED_WIDTH = 2

# Setup the Simulation

current_time = 0
delta_t = 0.1

lanes = [
    lane.Lane('SOUTH'),
    lane.Lane('SOUTH'),
    lane.Lane(),
    lane.Lane(),
]

lights = [
    trafficlight.TrafficLight(100),
    trafficlight.TrafficLight(200),
    trafficlight.TrafficLight(300),
    trafficlight.TrafficLight(400),
]


car2 = car.Car(150, 0, 0, 0)
car3 = car.Car(50, 0, 0, 0)
car4 = car.Car(150, 0, 0, 0)
car1a = car.Car(50, 0, 0, 0)
car1b = car.Car(60, 0, 10, 0)
car1c = car.Car(70, 0, 0, 0)
car1d = car.Car(90, 0, 0, 0)
lanes[0].add_car(car1a)
lanes[0].add_car(car1b)
lanes[0].add_car(car1c)
lanes[0].add_car(car1d)
lanes[0].add_car(car2)
lanes[2].add_car(car3)
lanes[3].add_car(car4)

cars = [car1a, car1b, car1c, car1d, car2, car3, car4]


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

def draw_data():
    pass

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

def get_color(car):
    return RED

def draw_car(car, direction, lane_number):
    start = START_MARGIN if direction == 1 else SCREEN_WIDTH - START_MARGIN
    pygame.draw.rect(
        screen, get_color(car),
        pygame.Rect(
            start + car.position * SCALE_METERS_TO_SCREEN * direction,
            STATS_HEIGHT + LANE_WIDTH * lane_number + CAR_MARGIN,
            CAR_HEIGHT,
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

def advance_cars(lanes):
    for lane in lanes:
        for car in lane.cars:
            control.advance(car, lane, lights, current_time, delta_t)

while True:
    for event in pygame.event.get():
        if event.type == pg.QUIT:
            sys.exit()
    screen.fill(WHITE)
    advance_cars(lanes)
    draw_data()
    draw_lanes(lanes)
    draw_cars(lanes)

    pygame.display.update()

