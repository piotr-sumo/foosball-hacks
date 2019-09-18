from unittest import main, TestCase
from unittest.mock import Mock
from sensors_and_state import MasterStateListener, UnknownGameModeException, ScoreBasedGameInProgressStateListener


class SensorsAndStateTest(TestCase):

    def test_should_fail_on_unknown_mode(self):
        # given
        unknown_mode = "unknown"
        state = Mock()

        # expect
        with self.assertRaises(UnknownGameModeException):
            MasterStateListener(state, unknown_mode)


class ScoreBasedGameInProgressStateListenerTest(TestCase):

    @staticmethod
    def create_listener():
        parent = Mock()
        parent.state = Mock()
        return parent, ScoreBasedGameInProgressStateListener(parent)

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


if __name__ == "__main__":
    main()
