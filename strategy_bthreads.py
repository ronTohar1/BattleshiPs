from bppy import *
from util import BOARD_SIZE as bsize
from itertools import product
from gymnasium import spaces
import numpy as np

strategy_space = spaces.Box(low=0, high=1, shape=(bsize,bsize), dtype=np.float32)
bthreads_progress = {}

state = None

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
	"""Strategy to fire in the middle for the first BOARD_SIZE^2/20 moves (5 moves)"""
	name = "Fire_In_Middle"
	reset_strategy(name)

	num_moves = bsize**2 // 10 # 10 for 10x10 board - number of moves this strategy will be active
	left_up, down_right = 2, bsize-3 # (2,2) to (7,7) for 10x10 board
	moves = [(x,y) for x in range(left_up, down_right+1) for y in range(left_up, down_right+1)]
	events = bevent_wrapper(moves)

	strategy = get_new_space()
	for move in moves:
		strategy[move] = 1	
	update_strategy(name, strategy)

	previous_moves = []
	for i in range(num_moves):
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		if action in moves and not action in previous_moves:
			previous_moves.append(action)
			strategy[action] = 0
			update_strategy(name, strategy)
		else:
			reset_strategy(name)
			return 
		
		# hit_cells, not_hit_cells = state[0], state[1]


@b_thread
def dont_fire_if_missed_twice_in_segment():
	"""This strategy goes up if we shoot a segment third time (which we already missed twice)"""
	name = "dont_fire_if_missed_twice_in_segment"
	prev_action = None
	prev_prev_action = None
	reset_strategy(name)
	strategy = get_strategy(name)
	# segment 0 - (0,0) to (4,4), segment 1 - (0,5) to (4,9), segment 2 - (5,0) to (9,4), segment 3 - (5,5) to (9,9)
	segments = [((0,0),(4,4)), ((0,5),(4,9)), ((5,0),(9,4)), ((5,5),(9,9))]
	
	def get_segment(a):
		# retrun the segment number of the action
		for i, segment in enumerate(segments):
			if segment[0][0] <= a[0] <= segment[1][0] and segment[0][1] <= a[1] <= segment[1][1]:
				return i

	def same_segment(a1,a2):
		return get_segment(a1) == get_segment(a2)

	while True:
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		reset_strategy(name) # reset strategy every time so it wont be active for more than 1 move
		hit_cells, not_hit_cells = state[0], state[1]
		if not (prev_action and prev_prev_action):
			prev_action = action
			prev_prev_action = prev_action
			continue
		if same_segment(prev_action, prev_prev_action):
			if not_hit_cells[prev_action] == 1 and not_hit_cells[prev_prev_action] == 1:
				segment = get_segment(prev_action)
				segment_range = segments[segment]
				# mark every possible action in the segment as 1 (dont fire there)
				for x,y in product(range(segment_range[0][0], segment_range[1][0]+1), range(segment_range[0][1], segment_range[1][1]+1)):
					strategy[x,y] = 1
		
		prev_action = action
		prev_prev_action = prev_action
		update_strategy(name, strategy)

@b_thread
def dont_fire_same_place():
	"""This strategy goes up if we shoot the same place twice"""
	name = "dont_fire_same_place"
	reset_strategy(name)
	strategy_space = get_strategy(name)
	while True:
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		strategy_space[action] = 1
		reset_strategy(name)

@b_thread
def dont_fire_pairs():
	"""This strategy goes up if we, in the first 20 moves, hit a pair of cells.
	This is because we want to spread our fire, and shoot in places that differ by
	the size of the smallest ship (2)"""
	name = "dont_fire_pairs"
	num_moves = bsize**2 // 5
	previous_action = None
	reset_strategy(name)
	strategy_space
	for i in range(num_moves):
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)

		hit_cells, not_hit_cells = state[0], state[1]
		if previous_action and not_hit_cells[action[0]][action[1]] == 1:
			if previous_action[0] == action[0] or previous_action[1] == action[1]:
				add_progress(name)
		else:
			kill_progress(name)
		previous_action = action


# # Not finished!
# def focus_on_one_ship():
# 	"""	This strategy goes up if we hit a ship, and we then fire around the area we hit, in order
# 	  	to encourage focusing a single ship to drown.
# 		We will try hitting 2 other cells that are adjacent. 
# 	"""
# 	name = "focus_on_one_ship"
# 	previous_action = None
# 	reset_progress(name)
# 	def distance(a1,a2):
# 		return abs(a1[0]-a2[0]) + abs(a1[1]-a2[1])
# 	while True:
# 		event = yield {waitFor: pred_all_events}
# 		action = get_tuple_action(event.name)
# 		hit_cells, not_hit_cells = state[0], state[1]
# 		if not previous_action:
# 			previous_action = action
# 		elif hit_cells[previous_action[0]][previous_action[1]] == 1: # if we hit a ship
# 			if distance(previous_action, action) == 1: # if we hit a cell adjacent to the previous action
# 				if hit_cells[action[0]][action[1]] == 0:
# 					add_progress(name) # good move and keep trying another adjacent cell next time
# 					previous_action = action
# 				else: # Not hit a ship - try again and focus on the previous place that got hit
# 					pass # dont change previous action because we want to focus on the place we hit
# 			else:
# 				kill_progress(name)
# 				previous_action = action



strategies_bts = [fire_in_middle,
		  		dont_fire_if_missed_twice_in_segment,
				]
# strategies_bts = [	fire_in_middle,
# 		  			dont_fire_if_missed_twice_in_segment,
# 					dont_fire_pairs,
# 					focus_on_one_ship
# 				]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts] + [request_all_moves()]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
