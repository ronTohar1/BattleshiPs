from bppy import *
from bp_wrapper import BPwrapper
from strategy_bthreads import *

class Dude:
    def __init__(self,y):
        self.x = 5
        self.y = y.x

def main():
    bthreads = create_strategies()
    bprog = BProgram(bthreads=bthreads, event_selection_strategy=SimpleEventSelectionStrategy(), listener=PrintBProgramRunnerListener())
    bpw = BPwrapper()
    bpw.reset(bprog)
    while True:
        bpw.advance_randomly()
    # bprog.run()
    # bpw.advance_randomly()


if __name__ == '__main__':
    main()