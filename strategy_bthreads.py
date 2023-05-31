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
	# if not strategy_space.contains(space):
	# 	if np.can_cast(space.dtype, np.float32):
	# 		raise Exception("space is not of type float32 and cannot be casted", space.dtype)
		
	# 	raise Exception(f"Strategy space does not contain the space given\nspace - {space}, strategy_space - {strategy_space}, shape = {space.shape},{strategy_space.shape}")
	bthreads_progress[name] = space

# put array of -1 in all places
# def kill_strategy(name):
# 	bthreads_progress[name] = np.array([[-1 for _ in range(bsize)] for _ in range(bsize)])

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



			

strategies_bts = [ request_all_moves(),
		  
					]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts] + [request_all_moves()]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
