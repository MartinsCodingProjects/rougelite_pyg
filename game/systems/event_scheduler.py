import time
import heapq

# create a eventschdeuler with a heap queue


class EventScheduler:
    def __init__(self):
        # priority queue of (time, event) tuples
        self.event_queue = []

    def schedule_event(self, event_time: float, event: callable) -> None:
        """Schedule an event to occur at a specific time (epoch seconds)"""
        heapq.heappush(self.event_queue, (event_time, event))

    def run_pending(self, game_time) -> None:
        """Run all events that are scheduled to occur up to the current time"""
        current_time = game_time
        while self.event_queue and self.event_queue[0][0] <= current_time:
            event_time, event = heapq.heappop(self.event_queue)
            event()  # execute the event callable

    def clear(self) -> None:
        """Clear all scheduled events"""
        self.event_queue = []
