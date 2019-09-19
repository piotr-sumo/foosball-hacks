from unittest import main, TestCase
from unittest.mock import Mock
from sensors_and_state import MasterStateListener, UnknownGameModeException, ScoreBasedGameInProgressStateListener, \
    TimeBasedGameInProgressStateListener, MAX_SCORE_GAME_MODE, WaitingForNewGameStateListener
from state import State
from time import sleep


class SensorsAndStateTest(TestCase):

    max_goals = 3

    def test_should_fail_on_unknown_mode(self):
        # given
        unknown_mode = "unknown"
        state = Mock()

        # expect
        with self.assertRaises(UnknownGameModeException):
            MasterStateListener(state, unknown_mode)

    def test_should_wait_for_new_game_when_previous_game_ends(self):
        # given
        state = State()
        master = MasterStateListener(state, MAX_SCORE_GAME_MODE, self.max_goals)
        master.exit_red_ball()

        # when
        self.assertTrue(isinstance(master.current_listener, ScoreBasedGameInProgressStateListener))
        for _ in range(self.max_goals):
            master.enter_red_ball()

        # then
        self.assertTrue(isinstance(master.current_listener, WaitingForNewGameStateListener))

    def test_should_wait_for_new_game_when_players_stopped_playing(self):
        # given
        state = Mock()
        master = MasterStateListener(state, MAX_SCORE_GAME_MODE)
        master.exit_red_ball()

        # when
        self.assertTrue(isinstance(master.current_listener, ScoreBasedGameInProgressStateListener))
        master.still_red_ball()

        # then
        self.assertTrue(isinstance(master.current_listener, WaitingForNewGameStateListener))


class ScoreBasedGameInProgressStateListenerTest(TestCase):

    @staticmethod
    def get_max_goals():
        return 3

    @staticmethod
    def create_listener():
        parent = Mock()
        parent.state = Mock()
        return parent, ScoreBasedGameInProgressStateListener(parent,
                                                             ScoreBasedGameInProgressStateListenerTest.get_max_goals())

    def test_should_increase_blue_score(self):
        # given:
        parent, listener = self.create_listener()

        # when
        listener.enter_blue_ball()

        # then
        self.assertTrue(parent.state.blue_scores.call_count == 1)

    def test_should_increase_red_score(self):
        # given:
        parent, listener = self.create_listener()

        # when
        listener.enter_red_ball()

        # then
        self.assertTrue(parent.state.red_scores.call_count == 1)

    def test_should_call_parent_on_premature_game_end_blue_team(self):
        # given
        parent, listener = self.create_listener()

        # when
        listener.still_blue_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_call_parent_on_premature_game_end_red_team(self):
        # given
        parent, listener = self.create_listener()

        # when
        listener.still_red_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_call_parent_when_blue_wins(self):
        # given
        parent, listener = self.create_listener()
        parent.state = State()

        # when
        for _ in range(self.get_max_goals()):
            listener.enter_blue_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_call_parent_when_red_wins(self):
        # given
        parent, listener = self.create_listener()
        parent.state = State()

        # when
        for _ in range(self.get_max_goals()):
            listener.enter_red_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)


class TimeBasedGameInProgressStateListenerTest(TestCase):

    @staticmethod
    def get_game_length():
        return 2

    @staticmethod
    def create_listener():
        parent = Mock()
        parent.state = Mock()
        return parent, TimeBasedGameInProgressStateListener(parent,
                                                            TimeBasedGameInProgressStateListenerTest.get_game_length())

    def test_should_call_parent_on_premature_game_end_blue_team(self):
        # given
        parent, listener = self.create_listener()

        # when
        listener.still_blue_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_call_parent_on_premature_game_end_red_team(self):
        # given
        parent, listener = self.create_listener()

        # when
        listener.still_red_ball()

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_increase_blue_score(self):
        # given:
        parent, listener = self.create_listener()

        # when
        listener.enter_blue_ball()

        # then
        self.assertTrue(parent.state.blue_scores.call_count == 1)

    def test_should_increase_red_score(self):
        # given:
        parent, listener = self.create_listener()

        # when
        listener.enter_red_ball()

        # then
        self.assertTrue(parent.state.red_scores.call_count == 1)

    def test_should_call_parent_when_blue_wins(self):
        # given
        parent, listener = self.create_listener()
        parent.state = State()

        # when
        listener.enter_blue_ball()
        sleep(self.get_game_length() + 1)  # warning, may be flaky

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)

    def test_should_call_parent_when_red_wins(self):
        # given
        parent, listener = self.create_listener()
        parent.state = State()

        # when
        listener.enter_red_ball()
        sleep(self.get_game_length() + 1)  # warning, may be flaky

        # then
        self.assertTrue(parent.game_has_ended.call_count == 1)


if __name__ == "__main__":
    main()
