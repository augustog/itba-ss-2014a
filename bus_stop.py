class BusStop(object):

    def __init__(self, position):
        self.position = position
        self.people = 0

    def person_arrived(self):
        self.people += 1

    def bus_arrived(self, bus):
        max_people = bus.max_people - bus.people_carried
        if self.people <= max_people:
            people = self.people
            self.people = 0
            return people
        self.people -= max_people
        return max_people
