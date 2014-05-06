class Lane(object):

    def __init__(self, way='NORTH'):
        self.cars = []
        self.way = way
        self.exclusive = False

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        self.cars.remove(car)

