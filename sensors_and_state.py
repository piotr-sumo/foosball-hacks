from sensors import SensorListener, PrintingListener
import sched
from threading import Thread

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
        print("exit_red_ball WaitingForNewGameStateListener")
        self.start_new_game()

    def start_new_game(self):
        self.parent_listener.state.reset()
        self.parent_listener.game_started()


class TimeBasedGameInProgressStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener
        self.thread = Thread(target=self.thread_main, daemon=True)
        self.game_in_progress = True

    def thread_main(self):
        s = sched.scheduler()
        s.enter(GAME_LENGTH, 1, self.game_has_ended)
        s.run()

    def game_has_ended(self):
        if self.game_in_progress:
            print("Timer has fired, game has ended")
            current_score = self.parent_listener.state.get_current_score()
            print("Game has ended", current_score)
            self.parent_listener.game_has_ended()

    def enter_blue_ball(self):
        print("enter_blue_ball TimeBasedGameInProgressStateListener")
        self.parent_listener.state.blue_scores()

    def enter_red_ball(self):
        print("enter_red_ball TimeBasedGameInProgressStateListener")
        self.parent_listener.state.blue_scores()

    def still_blue_ball(self):
        print("still_blue_ball TimeBasedGameInProgressStateListener")
        self.game_in_progress = False
        self.parent_listener.game_has_ended()

    def still_red_ball(self):
        print("still_red_ball TimeBasedGameInProgressStateListener")
        self.game_in_progress = False
        self.parent_listener.game_has_ended()


class ScoreBasedGameInProgressStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener

    def enter_blue_ball(self):
        print("enter_blue_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.state.blue_scores()
        self.check_game_progress()

    def enter_red_ball(self):
        print("enter_red_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.state.red_scores()
        self.check_game_progress()

    def still_red_ball(self):
        print("still_red_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.game_has_ended()

    def still_blue_ball(self):
        print("still_blue_ball ScoreBasedGameInProgressStateListener")
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


class UnknownGameModeException(Exception):
    def __init__(self, unknown_mode):
        super().__init__("Unknown game mode %s" % unknown_mode)


class MasterStateListener(SensorListener):
    def __init__(self, state, game_mode):
        self.state = state
        if game_mode not in [TIMED_GAME_MODE, MAX_SCORE_GAME_MODE]:
            raise UnknownGameModeException(game_mode)
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
        if self.game_mode == MAX_SCORE_GAME_MODE:
            self.current_listener = ScoreBasedGameInProgressStateListener(self)
        elif self.game_mode == TIMED_GAME_MODE:
            self.current_listener = TimeBasedGameInProgressStateListener(self)

    def game_has_ended(self):
        print("Game over", self.state.get_current_score())
        self.current_listener = WaitingForNewGameStateListener(self)
