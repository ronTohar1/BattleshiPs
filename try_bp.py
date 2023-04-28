from bppy import *
from bp_wrapper import BPwrapper
from strategy_bthreads import *


def main():
    bthreads = create_strategies()
    bprog = BProgram(bthreads=bthreads, event_selection_strategy=SimpleEventSelectionStrategy(), listener=PrintBProgramRunnerListener())
    bpw = BPwrapper()
    bpw.reset(bprog)
    print("Resetted bprog")
    while True:
        bpw.advance_randomly()
    # bprog.run()
    # bpw.advance_randomly()

if __name__ == '__main__':
    main()