from bppy import *
from bp_wrapper import BPwrapper
from strategy_bthreads import *


def main():
    bthreads = create_strategies()
    bprog = BProgram(bthreads=bthreads, event_selection_strategy=SimpleEventSelectionStrategy(), listener=PrintBProgramRunnerListener())
    bpw = BPwrapper()
    bpw.reset(bprog)
    while True:
        bpw.advance_randomly()

main()