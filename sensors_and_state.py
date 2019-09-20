from sensors import SensorListener, PrintingListener
import sched
from threading import Thread
import logging

TIMED_GAME_MODE = "TIMED"
MAX_SCORE_GAME_MODE = "SCORE"
MAX_GOALS = 10
GAME_LENGTH = 16 * 60  # 16 minutes


class WaitingForNewGameStateListener(PrintingListener):
    def __init__(self, parent_listener):
        self.parent_listener = parent_listener

    def exit_blue_ball(self):
        logging.info("exit_blue_ball WaitingForNewGameStateListener")
        self.start_new_game()

    def exit_red_ball(self):
        logging.info("exit_red_ball WaitingForNewGameStateListener")
        self.start_new_game()

    def start_new_game(self):
        self.parent_listener.state.reset()
        self.parent_listener.game_started()


class TimeBasedGameInProgressStateListener(PrintingListener):
    def __init__(self, parent_listener, game_length):
        self.parent_listener = parent_listener
        self.thread = Thread(target=self.thread_main, daemon=True)
        self.game_in_progress = True
        self.game_length = game_length
        self.thread.start()

    def thread_main(self):
        s = sched.scheduler()
        s.enter(self.game_length, 1, self.game_has_ended)
        s.run()

    def game_has_ended(self):
        if self.game_in_progress:
            logging.info("Timer has fired, game has ended")
            current_score = self.parent_listener.state.get_current_score()
            logging.info("Game has ended %s", current_score)
            self.parent_listener.game_has_ended()

    def enter_blue_ball(self):
        logging.info("enter_blue_ball TimeBasedGameInProgressStateListener")
        self.parent_listener.state.blue_scores()

    def enter_red_ball(self):
        logging.info("enter_red_ball TimeBasedGameInProgressStateListener")
        self.parent_listener.state.red_scores()

    def still_blue_ball(self):
        logging.info("still_blue_ball TimeBasedGameInProgressStateListener")
        self.game_in_progress = False
        self.parent_listener.game_has_ended()

    def still_red_ball(self):
        logging.info("still_red_ball TimeBasedGameInProgressStateListener")
        self.game_in_progress = False
        self.parent_listener.game_has_ended()


class ScoreBasedGameInProgressStateListener(PrintingListener):
    def __init__(self, parent_listener, max_score):
        self.parent_listener = parent_listener
        self.max_score = max_score

    def enter_blue_ball(self):
        logging.info("enter_blue_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.state.blue_scores()
        self.check_game_progress()

    def enter_red_ball(self):
        logging.info("enter_red_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.state.red_scores()
        self.check_game_progress()

    def still_red_ball(self):
        logging.info("still_red_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.game_has_ended()

    def still_blue_ball(self):
        logging.info("still_blue_ball ScoreBasedGameInProgressStateListener")
        self.parent_listener.game_has_ended()

    def game_has_ended(self, team):
        logging.info("%s team wins!", team)
        self.parent_listener.game_has_ended()

    def check_game_progress(self):
        current_score = self.parent_listener.state.get_current_score()
        if current_score.get_red_goals() == self.max_score:
            self.game_has_ended("Red")
        elif current_score.get_blue_goals() == self.max_score:
            self.game_has_ended("Blue")


class UnknownGameModeException(Exception):
    def __init__(self, unknown_mode):
        super().__init__("Unknown game mode %s" % unknown_mode)


class MasterStateListener(SensorListener):
    def __init__(self, state, game_mode, max_score=MAX_GOALS, max_game_length=GAME_LENGTH):
        self.state = state
        if game_mode not in [TIMED_GAME_MODE, MAX_SCORE_GAME_MODE]:
            raise UnknownGameModeException(game_mode)
        self.game_mode = game_mode
        self.current_listener = WaitingForNewGameStateListener(self)
        self.max_score = max_score
        self.max_game_length = max_game_length

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
        logging.info("Game started")
        if self.game_mode == MAX_SCORE_GAME_MODE:
            self.current_listener = ScoreBasedGameInProgressStateListener(self, self.max_score)
        elif self.game_mode == TIMED_GAME_MODE:
            self.current_listener = TimeBasedGameInProgressStateListener(self, self.max_game_length)
        self.state.game_started()

    def game_has_ended(self):
        logging.info("Game over %s", self.state.get_current_score())
        self.state.game_over()
        self.current_listener = WaitingForNewGameStateListener(self)

    def change_game_mode(self):
        if self.game_mode == TIMED_GAME_MODE:
            self.game_mode = MAX_SCORE_GAME_MODE
        else:
            self.game_mode = TIMED_GAME_MODE
