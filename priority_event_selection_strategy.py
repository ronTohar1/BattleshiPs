import random
from collections.abc import Iterable

from bppy.model.b_event import BEvent
from bppy.model.event_selection.event_selection_strategy import EventSelectionStrategy
from bppy.model.event_set import EmptyEventSet

MIN_PRIORITY = 0
MAX_PRIORITY = 100


class EventCollection:
	""" Collecting events and their priority in a dictionary, where each
	 entry is constructed of key - event, and value - priority.
	 e.g, {e1: 10, e2:20, e3:4.......}"""
	def __init__(self):
		self.events = {}

	def append(self, event: BEvent, priority):
		""" Adding the event to the event-priority dictionary.
		 If current event in dictionary, choosing the highest priority (existent or new)."""
		if event in self.events:
			if priority > self.events[event]:
				self.events[event] = priority
		else:
			self.events[event] = priority

	def add_many(self, events, priority):
		for event in events:
			self.append(event, priority)

	def discard_event(self, event):
		self.events.pop(event)

	def group_high_priority(self):
		""" Taking the events with the highest priority and returns them in a group """
		group = []
		if self.events:
			top_priority = MIN_PRIORITY
			for curr_priority in self.events.values():
				if curr_priority > top_priority:
					top_priority = curr_priority
			for ep in self.events.items():
				if ep[1] == top_priority:
					group.append(ep[0])

			return group
		else:
			return None


class PriorityEventSelectionStrategy(EventSelectionStrategy):
	def __init__(self):
		self.event_collection: EventCollection = None

	def is_satisfied(self, event, statement):
		if isinstance(statement.get('request'), BEvent):
			if isinstance(statement.get('waitFor'), BEvent):
				return statement.get('request') == event or statement.get('waitFor') == event
			else:
				return statement.get('request') == event or statement.get('waitFor', EmptyEventSet()).__contains__(
					event)
		else:
			if isinstance(statement.get('waitFor'), BEvent):
				return statement.get('request', EmptyEventSet()).__contains__(event) or statement.get(
					'waitFor') == event
			else:
				return statement.get('request', EmptyEventSet()).__contains__(event) or statement.get('waitFor',
				                                                                                      EmptyEventSet()).__contains__(
					event)

	def selectable_events(self, statements):
		possible_events: EventCollection = EventCollection()

		for statement in statements:
			statement_priority = self.get_statement_priority(statement)
			if 'request' in statement:  # should be eligible for sets
				if isinstance(statement['request'], Iterable):
					possible_events.add_many(statement['request'], statement_priority)
				elif isinstance(statement['request'], BEvent):
					possible_events.append(statement['request'], statement_priority)
				else:
					raise TypeError("request parameter should be BEvent or iterable")
		for statement in statements:
			if 'block' in statement:
				if isinstance(statement.get('block'), BEvent):
					possible_events.discard_event(statement.get('block'))
				else:
					events_to_delete = []
					for x in possible_events.events.items():
						if x[0] in statement.get('block'):
							events_to_delete.append(x[0])
					# Another loop for deleting, because cant delete during for loop.
					for event in events_to_delete:
						possible_events.discard_event(event)

		self.event_collection = possible_events
		return [x[0] for x in possible_events.events.items()]  # Returning the highest priority events

	def select(self, statements):
		events = self.selectable_events(statements)
		if events:
			highest_priority = self.event_collection.group_high_priority()
			return random.choice(tuple(highest_priority))
		else:
			return None

	def get_statement_priority(self, statement):
		""" Returns a statement priority.
		 If the statement has no priority, it will be the minimum one"""
		return statement.get('priority', MIN_PRIORITY)

# def max_priority_group(self, statements):
# 	""" Grouping the highest priority statements in one group and return it """
# 	group = []
# 	priority = 0
# 	for statement in statements:
# 		# Checking what is the statement's priority:
# 		if 'priority' in statement:
# 			curr_pri = statement.get('priority')
# 		else:
# 			curr_pri = 0
#
# 		if not np.isscalar(curr_pri) or not (MIN_PRIORITY <= curr_pri <= MAX_PRIORITY):
# 			raise Exception("Priority must be between {} and {}".format(MIN_PRIORITY, MAX_PRIORITY))
#
# 		# Adding the statement to its group if needed
# 		if curr_pri > priority:
# 			group = [statement]
# 			priority = curr_pri
# 		elif curr_pri == priority:
# 			group.append(statement)
#
# 	return group
