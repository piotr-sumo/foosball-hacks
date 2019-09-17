from time import sleep
import gpiozero.pins.mock
from sensors import Sensors, SensorListener
from sounds import ScoresStateListener
import sched

from game_generator import GameGenerator
from state import State


class PrintingListener(SensorListener):

    def enter_red_ball(self):
        print("enter_red_ball", type(self))

    def enter_blue_ball(self):
        print("enter_blue_ball", type(self))

    def exit_red_ball(self):
        print("exit_red_ball", type(self))

    def exit_blue_ball(self):
        print("exit_blue_ball", type(self))

    def still_red_ball(self):
        print("still_red_ball", type(self))

    def still_blue_ball(self):
        print("still_blue_ball", type(self))


TIMED_GAME_MODE = "TIMED"
MAX_SCORE_GAME_MODE = "SCORE"
MAX_GOALS = 10
GAME_LENGTH = 16 * 60  # 16 minutes


class WaitingForNewGameStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener

    def exit_blue_ball(self):
        print("exit_blue_ball WaitingForNewGameStateListener")
        self.start_new_game()

    def exit_red_ball(self):
        print("exit_blue_ball WaitingForNewGameStateListener")
        self.start_new_game()

    def start_new_game(self):
        self.parent_listener.state.reset()
        self.parent_listener.game_started()


class TimeProgressStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener
        s = sched.scheduler()
        s.enter(GAME_LENGTH, 1, self.game_has_ended)

    def game_has_ended(self):
        print("Timer has fired, game has ended")
        current_score = self.parent_listener.state.get_current_score()
        print("Game has ended", current_score)
        self.parent_listener.game_has_ended()

    def enter_blue_ball(self):
        print("enter_blue_ball GameInProgressStateListener")
        self.parent_listener.state.blue_scores()

    def enter_red_ball(self):
        print("enter_red_ball GameInProgressStateListener")
        self.parent_listener.state.blue_scores()


class ScoreGameInProgressStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener

    def enter_blue_ball(self):
        print("enter_blue_ball GameInProgressStateListener")
        self.parent_listener.state.blue_scores()
        self.check_game_progress()

    def enter_red_ball(self):
        print("enter_red_ball GameInProgressStateListener")
        self.parent_listener.state.blue_scores()
        self.check_game_progress()

    def still_red_ball(self):
        print("still_red_ball GameInProgressStateListener")
        self.parent_listener.game_has_ended()

    def still_blue_ball(self):
        print("still_blue_ball GameInProgressStateListener")
        self.parent_listener.game_has_ended()

    def game_has_ended(self, team):
        print(team, "team wins!")
        self.parent_listener.game_has_ended()

    def check_game_progress(self):
        current_score = self.parent_listener.state.get_current_score()
        if current_score.get_red_goals() == MAX_GOALS:
            self.game_has_ended("Red")
        elif current_score.get_blue_goals() == MAX_GOALS:
            self.game_has_ended("Blue")


class MasterStateListener(SensorListener):
    def __init__(self, state, game_mode):
        self.state = state
        self.game_mode = game_mode
        self.current_listener = WaitingForNewGameStateListener(self)

    def enter_red_ball(self):
        self.current_listener.enter_red_ball()

    def enter_blue_ball(self):
        self.current_listener.enter_blue_ball()

    def still_blue_ball(self):
        self.current_listener.still_blue_ball()

    def still_red_ball(self):
        self.current_listener.still_red_ball()

    def exit_red_ball(self):
        self.current_listener.exit_red_ball()

    def exit_blue_ball(self):
        self.current_listener.exit_blue_ball()

    def game_started(self):
        print("Game started")
        if self.game_mode == TIMED_GAME_MODE:
            self.current_listener = TimeProgressStateListener(self)
        elif self.game_mode == MAX_SCORE_GAME_MODE:
            self.current_listener = ScoreGameInProgressStateListener(self)
        else:
            raise Exception("Unknown game mode %s" % self.game_mode)

    def game_has_ended(self):
        print("Game over", self.state.get_current_score())
        self.current_listener = WaitingForNewGameStateListener(self)


if __name__ == "__main__":
    state = State()
    gpiozero.Device.pin_factory = gpiozero.pins.mock.MockFactory()
    sensors = Sensors()
    gg = GameGenerator(sensors.goal_box_red_button, sensors.goal_box_blue_button, 6000, 6000, 10000, 1300, 2000, 2, 2)
    state_listener = MasterStateListener(state, MAX_SCORE_GAME_MODE)
    sounds_listener = ScoresStateListener(state)
    sensors.attach(state_listener)
    state.attach(sounds_listener)
    game = gg.start()
    game.join()

    print("Game score", state.get_current_score())
    print("Simulation has ended")
