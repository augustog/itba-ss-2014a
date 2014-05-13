import control
import car
import lane
import trafficlight
import time

lane = lane.Lane()

#c1 = car.Car(20, 0, 0, 0)
c2 = car.Car(90, 0, 0, 0)
# c3 = car.Car(110, 0, 0, 0)
# c4 = car.Car(180, 0, 0, 0)

lights = [
    trafficlight.TrafficLight(100),
    trafficlight.TrafficLight(200),
    trafficlight.TrafficLight(300),
    trafficlight.TrafficLight(400),
]

#lane.add_car(c1)
lane.add_car(c2)
# lane.add_car(c3)
# lane.add_car(c4)

t = 29
delta_t = 0.1
for i in range(1000):
    #control.advance(c1, lane, lights, t, delta_t)
    control.advance(c2, lane, lights, t, delta_t)
    # control.advance(c3, lane, lights, t, delta_t)
    # control.advance(c4, lane, lights, t, delta_t)
    #print c1
    print c2
    # print c3
    # print c4
    print map(lambda x: x.pretty_print(t), lights)
    t += delta_t
    time.sleep(0.1)
