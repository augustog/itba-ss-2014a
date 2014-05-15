import unittest

import control

from car import Car
from lane import Lane
from trafficlight import TrafficLight

class ControlTest(unittest.TestCase):

    def setUp(self):
        self.car = Car(200, 0, 0, 0)
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
        red_light = TrafficLight(200, 'Red')
        self.assertFalse(
            control.can_advance(self.car, self.lane, [red_light], 0)
        )

    def test_can_advance_on_green(self):
        light = TrafficLight(200)
        self.assertTrue(
            control.can_advance(self.car, self.lane, [light], 0)
        )

    def test_car_cant_advance_due_to_traffic(self):
        light = TrafficLight(200)
        other_car = Car(200 + Car.length, 0, 0, 0)
        self.lane.add_car(other_car)
        self.assertFalse(
            control.can_advance(self.car, self.lane, [light], 0)
        )
        # Cleanup
        self.lane.remove_car(other_car)

    def test_get_next_car_before_next_traffic_light_returns_car(self):
        light = TrafficLight(100)
        self.car.position = 20
        other_car = Car(80, 0, 0, 0)
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
        other_car = Car(120, 0, 0, 0)
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
        other_car = Car(220, 0, 0, 0)
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
        test_car = Car(0, 0, 5, 0)
        self.assertTrue(
            abs(control.get_target_time(test_car, 10) - 1.6108) < 0.0001
        )

    def test_get_target_time_reaching_max_speed(self):
        test_car = Car(0, 0, 5, 0)
        self.assertTrue(
            abs(control.get_target_time(test_car, 100) -
                (20.0 / 9 + 200.0 / 3) < 0.0001)
        )

    def test_advance(self):
        for i in range(1, 99):
            test_car = Car(i, 0, 0, 0)
            lane = Lane()
            lane.add_car(test_car)
            lights = [TrafficLight(100)]
            for j in range(500):
                control.advance(test_car, lane, lights, 30, 0.1)
            self.assertTrue(test_car.position < 100,
                    'Car starting at %d fail' % i)

    def test_advance_with_car_in_front(self):
        for i in range (1, 80):
            test_car_1 = Car(i, 0, 0, 0)
            test_car_2 = Car(i + 19, 0, 0, 0)
            lane = Lane()
            lane.add_car(test_car_1)
            lane.add_car(test_car_2)
            lights = [TrafficLight(100)]
            for j in range(500):
                control.advance(test_car_1, lane, lights, 30, 0.1)
                control.advance(test_car_2, lane, lights, 30, 0.1)
            self.assertTrue(test_car_1.position < 100,
                    'First car at %d fail' % i)
            self.assertTrue(test_car_2.position < 100,
                    'Second car at %d fails' % (i + 19))

if __name__ == '__main__':
    unittest.main()
