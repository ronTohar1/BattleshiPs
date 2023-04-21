from bppy import *

bthreads_progress = {}

def reset_progress(name):
	bthreads_progress[name] = 0

def add_progress(name):
	bthreads_progress[name] += 1


all_events = EventSet(lambda event: True)

@b_thread
def request_all_moves():
	name = "requester"
	moves = ["e2", "e8", "e4", "e6", "c3v", "d3v", "e3v", "f3v"]
	moves = mirror_moves(moves)
	moves = [BEvent(m) for m in moves]
	while True:
		event = yield {request: moves}


@b_thread
def shiller_opening():
	name = "Shiller"
	# moves = ["e2", "e8", "e4", "e6", ["c3v", "d3v", "e3v", "f3v"]]
	moves = ["e2", "e8", "e4", "e6", "c3v", "d3v", "e3v", "f3v"]

	reset_progress(name)
	for move in moves:
		event = yield {waitFor: all_events}
		if True or event.name == move:
			print("Adding progress")
			add_progress(name)
		else:
			reset_progress()
			print("Resetted program")
			break




# strategies_bts = []
strategies_bts = [shiller_opening]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
