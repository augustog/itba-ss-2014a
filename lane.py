class Lane(object):

    def __init__(self):
        self.cars = []
        self.next = None
        self.prev = None
        self.exclusive = False
        self.index = 0

    def add_car(self, car):
        self.cars.append(car)

    def remove_car(self, car):
        self.cars.remove(car)

