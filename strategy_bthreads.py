from bppy import *
from util import BOARD_SIZE as bsize
from itertools import product

bthreads_progress = {}

state = None

def set_state(s):
	global state
	state = s

def reset_progress(name):
	bthreads_progress[name] = 0

def add_progress(name):
	bthreads_progress[name] += 1

def kill_progress(name):
	bthreads_progress[name] =- 1

def reset_all_progress():
	for name in bthreads_progress:
		reset_progress(name)

pred_all_events = EventSet(lambda event: True)

def bevent_wrapper(event_list):
	return [BEvent(str(event)) for event in event_list]

def get_tuple_action(action):
	if isinstance(action, str):
		action = eval(action) # should convert to int or tuple
	if isinstance(action, int):
		return (action % bsize, action // bsize)
	if not isinstance(action, tuple):
		raise Exception("Action must be tuple or int")
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
	num_moves = bsize**2 // 20
	left_up, down_right = 3, bsize-4 # (3,3) to (6,6) for 10x10 board
	moves = [(x,y) for x in range(left_up, down_right+1) for y in range(left_up, down_right+1)]
	events = bevent_wrapper(moves)
	previous_moves = []
	reset_progress(name)
	for i in range(num_moves):
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		print(f"Action: {action}")
		print('moves', moves)
		if action in moves and not action in previous_moves:
			previous_moves.append(action)
			add_progress(name)
		else:
			kill_progress(name)
			return 
		
		# hit_cells, not_hit_cells = state[0], state[1]


@b_thread
def dont_fire_if_missed_twice_in_segment():
	"""This strategy goes up if we hit a segment third time (which we already missed twice)"""
	name = "dont_fire_if_missed_twice_in_segment"
	segment_size = bsize//2 - 1 # 4 for 10x10 board
	prev_action = None
	prev_prev_action = None
	reset_progress(name)
	def perform_segment(a1,a2):
		# check if 2 actions perform a segment (are in distance of segment_size at most)
		return abs(a1[0]-a2[0]) <= segment_size and abs(a1[1]-a2[1]) <= segment_size
	
	while True:
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		hit_cells, not_hit_cells = state[0], state[1]
		if prev_action and prev_prev_action:
			# If previous action and current action missed:
			if not_hit_cells[previous_action[0]][previous_action[1]] == 1 and not_hit_cells[prev_prev_action[0]][prev_prev_action[1]] == 1:
				# if we are in the same segment:
				if perform_segment(prev_action, prev_prev_action):
					#  if the action is in the segment (in between the previous actions) - add progress
					if perform_segment(prev_action, action) and perform_segment(prev_prev_action, action):
						add_progress(name)
				
		previous_action = action
		prev_prev_action = previous_action



# strategies_bts = []
strategies_bts = [fire_in_middle]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts] + [request_all_moves()]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
