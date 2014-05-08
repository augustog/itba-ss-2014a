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


if __name__ == '__main__':
    unittest.main()
