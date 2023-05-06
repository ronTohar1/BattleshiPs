from bthreads_strategies import *

class BattleshipStrategy(BthreadStrategy):
    def __init__(self):
        super().__init__()
        self.strategies = []
        self.progress = {}
        for s in self.strategies:
            self.progress[s.name] = 0