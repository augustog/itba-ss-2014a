import math
import random

class Source(object):

    def __init__(self, estimated_time):
        self.cumm_time = 0
        self.triggered = False
        self.lambda_prob = 1.0 / estimated_time

    def chances_to_appear(self, delta_time):
        if self.triggered:
            return True
        t0 = self.cumm_time
        t1 = t0 + delta_time
        prob_0 = 1 - math.exp(-self.lambda_prob*t0)
        prob_1 = 1 - math.exp(-self.lambda_prob*t1)
        self.triggered = prob_0 < random.random() < prob_1
        return self.triggered

    def reset(self):
        self.triggered = False
        self.cumm_time = 0
