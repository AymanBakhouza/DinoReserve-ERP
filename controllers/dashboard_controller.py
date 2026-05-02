# controllers/dashboard_controller.py
from services.event_engine import EventResult, RandomEventEngine


class DashboardController:
    def __init__(self, current_user: dict):
        self.current_user = current_user
        self._events = RandomEventEngine()

    def trigger_random_event(self) -> EventResult:
        return self._events.trigger_random_event()
