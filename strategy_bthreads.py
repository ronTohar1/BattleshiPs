from enum import Enum
from bppy import *
from util import BOARD_SIZE as bsize, UPDATE_STATE as update_state
from itertools import product
from gymnasium import spaces
import numpy as np


# shared data - maybe something like {num_ships_found, num_2_size_found, found_5_size:True\False....} 
# And then bthreads can listen to those events (wait for update data event) and than look at the data.
# e.g found the 2 size ship, then no need to hit in distances of 2 only at 3 and more.

bthreads_progress = {}
state = None


# shared data options:
data = Enum('data',[
	'num_ships_found',
	'num_2_size_found',
	'num_5_size_found',
	'num_3_size_found',
	'num_4_size_found',
	'hit',
	'missed',
	'repeat',
] )


shared_data = dict()
for d in data:
	shared_data[d] = 0


def set_state(s):
	global state
	state = s

def get_new_space():
	return np.zeros((bsize, bsize))

def reset_strategy(name):
	bthreads_progress[name] = get_new_space()

def update_strategy(name, space):
	bthreads_progress[name] = space

def get_strategy(name):
	return bthreads_progress[name]

def reset_all_strategies():
	for name in bthreads_progress:
		reset_strategy(name)

def kill_strategy(name):
	reset_strategy(name)



pred_all_events = EventSet(lambda event: True)

def bevent_wrapper(event_list):
	return [BEvent(str(event)) for event in event_list]

def get_tuple_action(action):
	if isinstance(action, str):
		action = eval(action) # should convert to int or tuple
	if isinstance(action, np.int32) or isinstance(action, np.int64) or isinstance(action, int):
		return (action % bsize, action // bsize)
	if not isinstance(action, tuple):
		raise Exception("Action must be tuple or int, real type - ", type(action))
	return action

def adjacent_cells(action):
		"""return a list of adjacent cells to action (which are not out of bounds)"""
		x,y = action
		adjacent = [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]
		return [(x,y) for x,y in adjacent if 0 <= x < bsize and 0 <= y < bsize]

# We need this so we can choose any event, because bppy checks if event is selectable
@b_thread
def request_all_moves():
	name = "requester"
	moves = list(product(range(bsize), range(bsize)))
	moves = bevent_wrapper(moves)
	while True:
		event = yield {request: moves, waitFor: pred_all_events}


@b_thread
def fire_in_middle():
	name = "fire_in_middle"
	num_moves = bsize**2 // 10 # 10 for 10x10 board - number of moves this strategy will be active
	left_up, down_right = 2, bsize-3 # (2,2) to (7,7) for 10x10 board
	moves = [(x,y) for x in range(left_up, down_right+1) for y in range(left_up, down_right+1)]
	events = bevent_wrapper(moves)

	strategy = get_new_space()
	for move in moves:
		strategy[move] = 1	
	update_strategy(name, strategy)

	for i in range(num_moves):
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		if action in moves:
			strategy[action] = 0
			update_strategy(name, strategy)
		else:
			kill_strategy(name)
			return 


			

strategies_bts = [ fire_in_middle,
		  	
		  
					]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts] + [request_all_moves()]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
