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
	if isinstance(action, int) or isinstance(action, np.int32) or isinstance(action, np.int64):
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
	num_moves = bsize**2 // 10 # 5 for 10x10 board
	left_up, down_right = 2, bsize-3 # (2,2) to (7,7) for 10x10 board
	moves = [(x,y) for x in range(left_up, down_right+1) for y in range(left_up, down_right+1)]
	events = bevent_wrapper(moves)
	previous_moves = []
	reset_progress(name)
	for i in range(num_moves):
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
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
	segment_size = bsize//3 # 3 for 10x10 board
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
					#  if the action is in the same segment as the previous 2 actions: add progress
					if perform_segment(prev_action, action) and perform_segment(prev_prev_action, action):
						add_progress(name)
				
		previous_action = action
		prev_prev_action = previous_action

def dont_fire_pairs():
	"""This strategy goes up if we, in the first 20 moves, hit a pair of cells.
	This is because we want to spread our fire, and shoot in places that differ by
	the size of the smallest ship (2)"""
	name = "dont_fire_pairs"
	num_moves = bsize**2 // 5
	previous_action = None
	reset_progress(name)
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


# Not finished!
def focus_on_one_ship():
	"""	This strategy goes up if we hit a ship, and we then fire around the area we hit, in order
	  	to encourage focusing a single ship to drown.
		We will try hitting 2 other cells that are adjacent. 
	"""
	name = "focus_on_one_ship"
	previous_action = None
	reset_progress(name)
	def distance(a1,a2):
		return abs(a1[0]-a2[0]) + abs(a1[1]-a2[1])
	while True:
		event = yield {waitFor: pred_all_events}
		action = get_tuple_action(event.name)
		hit_cells, not_hit_cells = state[0], state[1]
		if not previous_action:
			previous_action = action
		elif hit_cells[previous_action[0]][previous_action[1]] == 1: # if we hit a ship
			if distance(previous_action, action) == 1: # if we hit a cell adjacent to the previous action
				if hit_cells[action[0]][action[1]] == 0:
					add_progress(name) # good move and keep trying another adjacent cell next time
					previous_action = action
				else: # Not hit a ship - try again and focus on the previous place that got hit
					pass # dont change previous action because we want to focus on the place we hit
			else:
				kill_progress(name)
				previous_action = action



# strategies_bts = []
strategies_bts = [	fire_in_middle,
		  			dont_fire_if_missed_twice_in_segment,
					dont_fire_pairs,
					focus_on_one_ship
				]

def create_strategies():
	# bthreads = [x() for x in strategies_bts + [request_all_moves()]]
    # bthreads = [request_all_moves()]
    bthreads = [x() for x in strategies_bts] + [request_all_moves()]
    return bthreads

def number_of_bthreads():
    # because of the request_all_moves which is not a strategy, but just there so we can choose any move
    return len(strategies_bts)
