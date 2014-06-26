from __future__ import division

import simulator as sim_module

from config import *

class TextListener(object):
    def pre_loop(self, simulator):
        pass
    def after_loop(self, simulator):
        print('Time: %.2f, Warmup: %s' % (
            simulator.current_time, 'Yes' if simulator.warmup else 'No'
        ))
        print('Cars: %d, Buses: %d' % (
            len(simulator.cars), len(simulator.buses)
        ))
        print('People on cars: %d, People on buses: %d' % (
            simulator.people_in_the_system_private,
            simulator.people_in_the_system_public
        ))
        if simulator.time_spent_public > 0 and simulator.time_spent_private > 0:
            print('Speed on cars: %d, Speed on buses: %d' % (
                simulator.meters_covered_private/simulator.time_spent_private,
                simulator.meters_covered_public/simulator.time_spent_public,
            ))
        print('Finished on cars: %d, Finished on buses: %d' % (
            simulator.people_finished_private,
            simulator.people_finished_public
        ))

sim = sim_module.Simulator(config_lanes, config_lines)
sim.add_listener(TextListener())

while True:
    sim.loop()
