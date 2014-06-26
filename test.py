import unittest

import control

from car import Car
from lane import Lane
from trafficlight import TrafficLight
from bus import Bus
from bus_line import BusLine
from bus_stop import BusStop

class ControlTest(unittest.TestCase):

    def setUp(self):
        self.car = Car(200, 0, 0, 0, 0)
        self.lane = Lane()
        self.lane.add_car(self.car)

    def test_next_in_set(self):
        self.assertEquals(
            control._next_in_set(3, [1, 2, 3, 4, 5], key = lambda x: x), 3
        )
        self.assertEquals(
            control._next_in_set(3, [1, 2, 3.5, 4, 5], key = lambda x: x), 3.5
        )

    def test_prev_in_set(self):
        self.assertEquals(
            control._prev_in_set(3, [1, 2, 3, 4, 5], key = lambda x: x), 3
        )
        self.assertEquals(
            control._prev_in_set(3, [1, 2.5, 3.5, 4, 5], key = lambda x: x), 2.5
        )

    def test_cant_advance_on_traffic_light(self):
        red_light = TrafficLight(200, initial_state='Red')
        self.assertFalse(
            control.can_advance(self.car, self.lane, [self.lane], [red_light], 0)
        )

    def test_can_advance_on_green(self):
        light = TrafficLight(200)
        self.assertTrue(
            control.can_advance(self.car, self.lane, [self.lane], [light], 0)
        )

    def test_car_cant_advance_due_to_traffic(self):
        light = TrafficLight(200)
        other_car = Car(200 + Car.length, 0, 0, 0, 0)
        self.lane.add_car(other_car)
        self.assertFalse(
            control.can_advance(self.car, self.lane, [self.lane], [light], 0)
        )
        # Cleanup
        self.lane.remove_car(other_car)

    def test_get_next_car_before_next_traffic_light_returns_car(self):
        light = TrafficLight(100)
        self.car.position = 20
        other_car = Car(80, 0, 0, 0, 0)
        self.lane.add_car(other_car)
        self.assertEquals(
            control.get_next_car_before_next_traffic_light(
                self.car, self.lane, [light]
            ), other_car
        )
        self.lane.remove_car(other_car)
        self.car.position = 200

    def test_get_next_car_before_next_traffic_light_returns_none(self):
        light = TrafficLight(100)
        self.car.position = 20
        other_car = Car(120, 0, 0, 0, 0)
        self.lane.add_car(other_car)
        self.assertFalse(
            control.get_next_car_before_next_traffic_light(
                self.car, self.lane, [light]
            )
        )
        self.lane.remove_car(other_car)
        self.car.position = 200

    def test_get_next_car_before_next_traffic_light_when_car_on_light(self):
        light = TrafficLight(200)
        other_car = Car(220, 0, 0, 0, 0)
        self.lane.add_car(other_car)
        self.assertFalse(
            control.get_next_car_before_next_traffic_light(
                self.car, self.lane, [light]
            )
        )
        self.lane.remove_car(other_car)

    def test_solve_quadratic_equation_with_one_negative_solution(self):
        self.assertEquals(control.solve_quadratic_equation(1, -3, -10), 5)

    def test_solve_quadratic_equation_with_one_solution(self):
        self.assertEquals(control.solve_quadratic_equation(1, -8, 16), 4)

    def test_solve_quadratic_equation_with_two_positive_solutions(self):
        self.assertEquals(control.solve_quadratic_equation(1, -7, 10), 2)

    def test_get_target_time_without_reaching_max_speed(self):
        test_car = Car(0, 0, 0, 5, 0)
        self.assertTrue(
            abs(control.get_target_time(test_car, 10) - 1.6108) < 0.0001
        )

    def test_get_target_time_reaching_max_speed(self):
        test_car = Car(0, 0, 0, 5, 0)
        self.assertTrue(
            abs(control.get_target_time(test_car, 100) -
                (20.0 / 9 + 200.0 / 3) < 0.0001)
        )

    def test_advance(self):
        for i in range(1, 99):
            test_car = Car(i, 0, 0, 0, 0)
            lane = Lane()
            lanes = [lane]
            lane.add_car(test_car)
            lights = [TrafficLight(100)]
            for j in range(200):
                control.advance(test_car, lane, lanes, lights, 30, 0.1)
            self.assertTrue(test_car.position < 100,
                    'Car starting at %d fail' % i)

    def test_advance_with_car_in_front(self):
        for i in range (1, 80):
            test_car_1 = Car(i, 0, 0, 0, 0)
            test_car_2 = Car(i + 19, 0, 0, 0, 0)
            lane = Lane()
            lanes = [lane]
            lane.add_car(test_car_1)
            lane.add_car(test_car_2)
            lights = [TrafficLight(100)]
            for j in range(200):
                control.advance(test_car_1, lane, lanes, lights, 30, 0.1)
                control.advance(test_car_2, lane, lanes, lights, 30, 0.1)
            self.assertTrue(test_car_1.position < 100,
                    'First car at %d fail, pos(car1) = %f, pos(car2) = %f'
                    %(i, test_car_1.position, test_car_2.position))
            self.assertTrue(test_car_2.position < 100,
                    'Second car at %d fails' % (i + 19))
            self.assertTrue(test_car_1.position <= control.rear(
                test_car_2, test_car_1.speed),
                'First car ended up further than expected'
            )

    def test_cant_change_lane_when_car_beside(self):
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(20, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_cant_change_lane_when_car_slightly_behind(self):
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(15, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_cant_change_lane_when_car_slightly_in_front(self):
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(25, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_cant_change_lane_when_close_to_traffic_lights(self):
	car1 = Car(98, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
        light = TrafficLight(100)
        self.assertFalse(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_cant_change_to_lane_with_opposite_direction(self):
        car = Car(20, 0, 0, 10, 0)
        lane1 = Lane()
        lane2 = Lane('SOUTH')
        light = TrafficLight(100)
        self.assertFalse(control.can_change_lane(car, lane1, lane2, [light]))

    def test_can_change_lane_when_alone(self):
	car1 = Car(20, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
        light = TrafficLight(100)
        self.assertTrue(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_can_change_lane_when_cars_around_but_far(self):
	car1 = Car(50, 0, 0, 10, 0)
	car2 = Car(20, 0, 0, 10, 0)
	car3 = Car(70, 0, 0, 10, 0)
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane2.add_car(car2)
	lane2.add_car(car3)
        light = TrafficLight(100)
        self.assertTrue(control.can_change_lane(car1, lane1, lane2, [light]))

    def test_shouldnt_change_lane_to_go_faster_when_nothing(self):
	car1 = Car(50, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
        light = TrafficLight(100)
        self.assertFalse(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]))

    def test_shouldnt_change_lane_to_go_faster_when_no_cars_in_front(self):
	car1 = Car(10, 0, 0, 10, 0)
	car0 = Car(50, 0, 0, 10, 0)
	car2 = Car(40, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane0.add_car(car0)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]))

    def test_should_change_lane_to_go_to_faster_lane(self):
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(30, 0, 0, 10, 0)
	car3 = Car(40, 0, 0, 10, 0)
	car4 = Car(35, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane1.add_car(car4)
	lane0.add_car(car2)
	lane2.add_car(car3)
        light = TrafficLight(100)
        self.assertEquals(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]), lane2)

    def test_should_change_lane_to_go_to_no_car_lane(self):
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(30, 0, 0, 10, 0)
	car3 = Car(60, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane1.add_car(car1)
	lane1.add_car(car3)
	lane0.add_car(car2)
        light = TrafficLight(100)
        self.assertEquals(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]), lane2)

    def test_shouldnt_change_lane_when_cant_change_lane(self):
        car0 = Car(18, 0, 0, 10, 0)
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(25, 0, 0, 10, 0)
        car3 = Car(23, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane0.add_car(car0)
	lane1.add_car(car1)
        lane1.add_car(car3)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]))

    def test_shouldnt_change_lane_when_current_lane_is_fastest(self):
        car0 = Car(30, 0, 0, 10, 0)
	car1 = Car(20, 0, 0, 10, 0)
	car2 = Car(45, 0, 0, 10, 0)
        car3 = Car(50, 0, 0, 10, 0)
        lane0 = Lane()
	lane1 = Lane()
	lane2 = Lane()
	lane0.add_car(car0)
	lane1.add_car(car1)
        lane1.add_car(car3)
	lane2.add_car(car2)
        light = TrafficLight(100)
        self.assertFalse(control.should_change_lane_to_move_faster(car1, lane1,
            [lane0, lane2], [light]))

    def test_bus_arrived_at_stop_at_full_capacity(self):
        lane = Lane()
        stop = BusStop(lane, 30, 10)
        line = BusLine([stop], 0, 500)
        bus = Bus(line, 10, 100)
        control.bus_stop(bus, stop)
        self.assertEquals(bus.people_carried, 100)
        self.assertEquals(stop.people, 10)

    def test_bus_arrived_and_people_were_left_at_stop(self):
        lane = Lane()
        stop = BusStop(lane, 30, 10)
        line = BusLine([stop], 0, 500)
        bus = Bus(line, 10, 93)
        control.bus_stop(bus, stop)
        self.assertEquals(bus.people_carried, 100)
        self.assertEquals(stop.people, 3)

    def test_bus_arrived_and_everybody_got_on_the_bus(self):
        lane = Lane()
        stop = BusStop(lane, 30, 10)
        line = BusLine([stop], 0, 500)
        bus = Bus(line, 10, 10)
        control.bus_stop(bus, stop)
        self.assertEquals(bus.people_carried, 20)
        self.assertEquals(stop.people, 0)

    def test_appear_cars_between_two_lanes(self):
        lanes = [Lane(), Lane()]
        lights = [TrafficLight(100)]

    def test_get_target_lanes(self):
        lanes = [Lane(), Lane(), Lane(), Lane(), Lane(), Lane(), Lane(), Lane()]
        self.assertEquals(control._get_target_lanes(lanes[3], lanes, 4, 4),
            [lanes[2], None])
        self.assertEquals(control._get_target_lanes(lanes[0], lanes, 4, 4),
            [None, lanes[1]])
        self.assertEquals(control._get_target_lanes(lanes[2], lanes, 4, 4),
            [lanes[1], lanes[3]])
        self.assertEquals(control._get_target_lanes(lanes[4], lanes, 4, 4),
            [None, lanes[5]])
        self.assertEquals(control._get_target_lanes(lanes[7], lanes, 4, 4),
            [lanes[6], None])

if __name__ == '__main__':
    unittest.main()
