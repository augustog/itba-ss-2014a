from config import *
import car
import bus


STRONG = 'Strong'
LIGHT = 'Light'
DOTTED = 'Dotted'

DOTTED_LENGTH = 50

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 500
START_MARGIN = 50
SCALE_METERS_TO_SCREEN = (SCREEN_WIDTH - 2 * START_MARGIN) / ROAD_LENGTH

TEXT_MARGIN = 10
TEXT_LINE_MARGIN = 5
STATS_HEIGHT = 200

CAR_WIDTH = car.Car.length / 2 * SCALE_METERS_TO_SCREEN
CAR_HEIGHT = car.Car.length * SCALE_METERS_TO_SCREEN

BUS_WIDTH = bus.Bus.length / 2 * SCALE_METERS_TO_SCREEN
BUS_HEIGHT = bus.Bus.length * SCALE_METERS_TO_SCREEN

LANE_WIDTH = 25
CAR_MARGIN = (LANE_WIDTH - CAR_HEIGHT) / 2
BUS_MARGIN = 10

TRAFFIC_LIGHT_RADIUS = 10
TRAFFIC_LIGHT_MARGIN = 20
DOTTED_WIDTH = 2

BUS_STOP_WIDTH = 10
