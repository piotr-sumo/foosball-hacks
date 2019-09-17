from time import sleep
from datetime import datetime
import requests


class StateListener:

    def event_happened(self, event):
        pass


class LoggingStateListener(StateListener):

    def event_happened(self, event):
        print("Received event:", event)


class SumoStateListener(StateListener):

    def __init__(self, source_url):
        self.source_url = source_url

    def event_happened(self, event):
        msg = f"Received event: {event.description()}"
        r = requests.post(self.source_url, data=msg)
        print("Sent request to sumo, got status", r.status_code)


class GameScore:
    def __init__(self, red_goals, blue_goals):
        self.red_goals = red_goals
        self.blue_goals = blue_goals

    def get_red_goals(self):
        return self.red_goals

    def get_blue_goals(self):
        return self.blue_goals

    def __str__(self):
        return f"Red {self.red_goals} goal(s). Blue {self.blue_goals} goal(s)."


class Event:
    def __init__(self, happened_at):
        self.happened_at = happened_at

    def kind(self):
        raise NotImplementedError()

    def description(self):
        return f"{self.kind()}: {self.happened_at}"

    def get_happened_at(self):
        return self.happened_at

    def __str__(self):
        return self.description()


class RedGoal(Event):
    def __init__(self, happened_at):
        super().__init__(happened_at)

    def kind(self):
        return "Red goal"


class BlueGoal(Event):
    def __init__(self, happened_at):
        super().__init__(happened_at)

    def kind(self):
        return "Blue goal"


class State:
    def __init__(self, listeners=[]):
        self.reset()
        self.listeners = listeners

    def reset(self):
        self.red_goals = 0
        self.blue_goals = 0
        self.event_log = []
        self.started_at = datetime.now()

    def __str__(self):
        return f"State: red goals {self.red_goals}; blue goals {self.blue_goals}; started at {self.started_at}"

    def get_event_log(self):
        return self.event_log

    def fire_listeners(self, event):
        for l in self.listeners:
            try:
                l.event_happened(event)
            except Exception as e:
                # TODO: listener name or something
                print("Listener failed", e)

    def blue_scores(self):
        self.blue_goals += 1
        e = BlueGoal(datetime.now())
        self.event_log.append(e)
        self.fire_listeners(e)

    def get_blue_goals(self):
        return self.blue_goals

    def red_scores(self):
        self.red_goals += 1
        e = RedGoal(datetime.now())
        self.event_log.append(e)
        self.fire_listeners(e)

    def get_red_goals(self):
        return self.red_goals

    def last_event_timestamp(self):
        if len(self.event_log) > 0:
            return self.event_log[-1].get_happened_at()
        else:
            return None

    def get_current_score(self):
        return GameScore(self.red_goals, self.blue_goals)


def create_sumo_listener():
    import json
    try:
        with open("config.json1") as config_file:
            config = json.load(config_file)
        return SumoStateListener(config["metadata"]["log_source_url"])
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    sumo_listener_opt = create_sumo_listener()
    if sumo_listener_opt is None:
        s = State()
    else:
        s = State([sumo_listener_opt])
    s.red_scores()
    sleep(2)
    s.blue_scores()
    print("Show state:", s)
    print("Show events:", ', '.join([str(x) for x in s.get_event_log()]))
    print("Last event timestamp:", s.last_event_timestamp())
    print("Correctly counts red goals:", s.get_red_goals() == 1)
    print("Correctly counts blue goals:", s.get_blue_goals() == 1)
    print("Current score", s.get_current_score())
    # WARNING, state reset here
    s.reset()
    print("Last event timestamp on an empty state:", s.last_event_timestamp())
    print("Correctly counts red goals on empty state:", s.get_red_goals() == 0)
    print("Correctly counts blue goals on empty state:", s.get_blue_goals() == 0)
    print("Done")
