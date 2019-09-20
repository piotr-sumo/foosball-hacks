from time import sleep
from datetime import datetime
import requests
import logging


logger = logging.getLogger("state")


class StateListener:

    def event_happened(self, event):
        pass


class LoggingStateListener(StateListener):

    def event_happened(self, event):
        logger.info("Received event:", event)


class SumoStateListener(StateListener):

    def __init__(self, source_url):
        self.source_url = source_url

    def event_happened(self, event):
        msg = f"Received event: {event.description()}"
        r = requests.post(self.source_url, data=msg)
        logger.info("Sent request to sumo, got status %s", r.status_code)


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


class GameOver(Event):
    def __init__(self, happened_at):
        super().__init__(happened_at)

    def kind(self):
        return "Game over"


class GameStarted(Event):
    def __init__(self, happened_at):
        super().__init__(happened_at)

    def kind(self):
        return "Game started"


class State:
    def __init__(self, listeners=[]):
        self.reset()
        self.listeners = listeners

    def reset(self):
        self.red_goals = 0
        self.blue_goals = 0
        self.event_log = []
        self.started_at = datetime.now()

    def attach(self, listener):
        self.listeners.append(listener)

    def detach(self, listener):
        self.listeners.remove(listener)

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
                logger.error("Listener failed", e)

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

    def game_over(self):
        e = GameOver(datetime.now())
        self.event_log.append(e)
        self.fire_listeners(e)

    def game_started(self):
        e = GameStarted(datetime.now())
        self.event_log.append(e)
        self.fire_listeners(e)


def create_sumo_listener():
    import json
    try:
        with open("config.json") as config_file:
            config = json.load(config_file)
        return SumoStateListener(config["metadata"]["log_source_url"])
    except FileNotFoundError:
        return None


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    sumo_listener_opt = create_sumo_listener()
    if sumo_listener_opt is None:
        s = State()
    else:
        s = State([sumo_listener_opt])
    s.red_scores()
    sleep(2)
    s.blue_scores()
    logger.info("Show state: %s", s)
    logger.info("Show events: %s", ', '.join([str(x) for x in s.get_event_log()]))
    logger.info("Last event timestamp: %s", s.last_event_timestamp())
    logger.info("Correctly counts red goals: %s", s.get_red_goals() == 1)
    logger.info("Correctly counts blue goals: %s", s.get_blue_goals() == 1)
    logger.info("Current score %s", s.get_current_score())
    # WARNING, state reset here
    s.reset()
    logger.info("Last event timestamp on an empty state: %s", s.last_event_timestamp())
    logger.info("Correctly counts red goals on empty state %s:", s.get_red_goals() == 0)
    logger.info("Correctly counts blue goals on empty state %s:", s.get_blue_goals() == 0)
    logger.info("Done")
