from bppy import *


class BthreadStrategy:
    def __init__(self):
        self.state = None
        self.progress = {}

    def __str__(self):
        return self.name
    
    def set_state(self, state):
        self.state = state
    
    def reset_progress(self, name):
        self.progress[name] = 0

    def add_progress(self, name):
        self.progress[name] += 1

    def reset_all_progress(self):
        for name in self.progress:
            self.reset_progress(name)

    