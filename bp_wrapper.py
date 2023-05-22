from bppy import *

# from eventsUtilities import EventHandler

# event_handler = EventHandler()


class BPwrapper():
	def __init__(self):
		self.ess: EventSelectionStrategy = None
		self.bprog: BProgram = None
		self.selectable_events = None
		self.tickets = None
		self.listener = None
		self.initialized = False

	def reset(self, bprogram: BProgram):
		self.bprog = bprogram
		self.bprog.setup()
		self.ess = self.bprog.event_selection_strategy
		self.tickets = self.bprog.tickets
		self.selectable_events = self.ess.selectable_events(self.tickets)
		self.listener = self.bprog.listener
		self.initialized = True

	def advance_randomly(self) -> BEvent:
		# if not self.is_game_finished():
			# chosen_event = random.choice(tuple(self.selectable_events))
			# self.choose_event(chosen_event)
			# return chosen_event

		chosen_event = self.ess.select(self.tickets)
		# print("selecteble events:", self.get_selectable_events())
		# print("Chose ", chosen_event)
		self.choose_event(chosen_event)
		return chosen_event

		# return None

	def choose_event(self, event: BEvent):
		if event not in self.selectable_events:
			raise Exception("Tried to choose blocked event!")
		self.listen(event)
		self.bprog.advance_bthreads(event)
		self.selectable_events = self.ess.selectable_events(self.tickets)

	# Just an idea for now, not sure if it's needed or possible.
	def choose_external_event(self, event: BEvent):
		pass

	def listen(self, event: BEvent):
		if self.listener:
			self.listener.event_selected(b_program=self.bprog, event=event)

	def get_selectable_events(self):
		return self.selectable_events

	# def is_game_finished(self):
	# 	""" Returns true if the game has finished.
	# 	If the last event available is the win event - choosing it."""

	# 	selectable = self.selectable_events
	# 	if selectable is None:
	# 		raise Exception("Selectable events is None")
	# 	if len(selectable) > 1:  # More than one possible event left.
	# 		return False
	# 	if len(selectable) == 1: # One event left - either win event or might be some other event available.
	# 		event = selectable[0]
	# 		game_finished = event_handler.is_game_finished_event(event)
	# 		if game_finished: # If game is finished - choosing the win event
	# 			self.choose_event(event)
	# 		return game_finished

	# 	return True # No events are selectable

