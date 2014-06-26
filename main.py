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
import simulator as sim_module
import source
import trafficlight

from config import *
from config_pygame import *


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 16)

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

def draw_data(simulator):
    y = TEXT_MARGIN
    time_text = font.render('Time: %.2f, Warmup: %s' % (
        simulator.current_time, 'Yes' if simulator.warmup else 'No'
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('Cars: %d, Buses: %d' % (
        len(simulator.cars), len(simulator.buses)
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('People on cars: %d, People on buses: %d' % (
        simulator.people_in_the_system_private,
        simulator.people_in_the_system_public
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    if simulator.time_spent_public > 0 and simulator.time_spent_private > 0:
        time_text = font.render('Speed on cars: %0.2f m/s, Speed on buses: %0.2f m/s' % (
            simulator.meters_covered_private/simulator.time_spent_private,
            simulator.meters_covered_public/simulator.time_spent_public,
        ), True, BLACK)
        screen.blit(time_text, (TEXT_MARGIN, y))
        y += time_text.get_height() + TEXT_LINE_MARGIN
    time_text = font.render('Finished on cars: %d (%0.2f P/m), Finished on buses: %d (%0.2f P/m)' % (
        simulator.people_finished_private,
        simulator.people_finished_private / (simulator.current_time - simulator.warmup_time) * 60,
        simulator.people_finished_public,
        simulator.people_finished_public / (simulator.current_time - simulator.warmup_time) * 60,
    ), True, BLACK)
    screen.blit(time_text, (TEXT_MARGIN, y))
    y += time_text.get_height() + TEXT_LINE_MARGIN
    return y

def draw_lanes(simulator, lanes, lights):
    first = True
    y = STATS_HEIGHT
    start = START_MARGIN
    end = SCREEN_WIDTH - START_MARGIN
    for i in range(0, len(lanes)):
        line_type = DOTTED
        if i == 0 or lanes[i].exclusive != lanes[i-1].exclusive:
            line_type = STRONG
        draw_line(line_type, start, end, y)
        y += LANE_WIDTH
        first = False
    draw_line(STRONG, start, end, y)
    for light in lights:
        pygame.draw.circle(screen,
            GREEN if light.is_green(simulator.current_time) else RED,
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

def draw_bus(bus, lane_number):
    start = START_MARGIN
    pygame.draw.rect(
        screen, YELLOW,
        pygame.Rect(
            start + bus.position * SCALE_METERS_TO_SCREEN,
            STATS_HEIGHT + LANE_WIDTH * lane_number + BUS_MARGIN,
            -BUS_HEIGHT, BUS_WIDTH
        )
    )
    people_count = small_font.render(str(bus.people_carried), True, BLACK)
    screen.blit(people_count, (
        start + bus.position * SCALE_METERS_TO_SCREEN - 2 * BUS_MARGIN,
        STATS_HEIGHT + LANE_WIDTH * lane_number + BUS_MARGIN / 2,
    ))

def draw_car(car, lane_number):
    start = START_MARGIN
    pygame.draw.rect(
        screen, get_color(car),
        pygame.Rect(
            start + car.position * SCALE_METERS_TO_SCREEN,
            STATS_HEIGHT + LANE_WIDTH * lane_number + CAR_MARGIN,
            -CAR_HEIGHT, CAR_WIDTH
        )
    )

def draw_bus_stops(simulator):
    start = START_MARGIN
    for index, line in enumerate(simulator.lines):
        for stop in line.bus_stops:
            people_count = small_font.render('(%d, %d)' % (index, stop.people), True, BLUE)
            screen.blit(people_count, (
                start + stop.position * SCALE_METERS_TO_SCREEN - 2 * BUS_STOP_WIDTH,
                STATS_HEIGHT - BUS_STOP_WIDTH,
            ))

def draw_cars(lanes):
    lane_number = 0
    for lane in lanes:
        for car in lane.cars:
            if isinstance(car, bus.Bus):
                draw_bus(car, lane_number)
            else:
                draw_car(car, lane_number)
        lane_number += 1

class PygameListener(object):

    def pre_loop(self, simulator):
        pass

    def after_loop(self, simulator):
        for event in pygame.event.get():
            if event.type == pg.QUIT:
                sys.exit()
        screen.fill(WHITE)
        draw_data(simulator)
        draw_lanes(simulator, simulator.lanes, simulator.lights)
        draw_cars(simulator.lanes)
        draw_bus_stops(simulator)
        pygame.display.update()


sim = sim_module.Simulator(config_lanes, config_lines)
sim.add_listener(PygameListener())

while True:
    sim.loop()
