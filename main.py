import pygame
import pygame.locals as pg

import car
import lane
import trafficlight
import control


pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((1200, 400))

STRONG = 'Strong'
LIGHT = 'Light'
DOTTED = 'Dotted'

DOTTED_LENGTH = 50

BLACK = (0, 0, 0)

def draw_line(line_type=STRONG, from_x=0, to_x=0, y=0, color=BLACK):
    if line_type == DOTTED:
        draw_dotted_line(from_x, to_x, y, color)
    else:
        width = 4 if line_type == STRONG else 2
        pygame.draw.line(screen, color, (from_x, y), (to_x, y), width)

def draw_dotted_line(from_x, to_x, y, color):
    for i in range(from_x, to_x, DOTTED_LENGTH):
        pygame.draw.line(
            screen, color, (i, y), (i + DOTTED_LENGTH / 2, y), width
        )

def draw_data():
    pass

STATS_HEIGHT = 100
CAR_WIDTH = 25
CAR_HEIGHT = 40
LANE_WIDTH = 40
CAR_MARGIN = 9
SCALE_METERS_TO_SCREEN = 10

def draw_lanes(lanes):
    first = True
    y = STATS_HEIGHT
    start = 50
    end = 1150
    for i in lanes
        first = False
        line_type = DOTTED
        if first or lanes[i].way != lanes[i-1].way:
            line_type = STRONG
        draw_line(line_type, start, end, y)
        y += LANE_WIDTH
    draw_line(STRONG, start, end, y)

def get_color(car):
    return (255, 0, 0)

def draw_car(car, lane_number):
    pygame.draw.rect(
        screen, get_color(car),
        pygame.Rect(
            START_MARGIN + car.position * SCALE_METERS_TO_SCREEN,
            STATS_HEIGHT + LANE_WIDTH * lane_number + CAR_MARGIN,
            CAR_HEIGHT,
            CAR_WIDTH
        )
    )

def draw_cars():
    pass

def advance_cars():
    pass

def print_screen():
    pass

while True:
    draw_data()
    draw_lanes()
    draw_cars()
    advance_cars()
    print_screen()

