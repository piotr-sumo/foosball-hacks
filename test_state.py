from state import State, StateListener, RedGoal, BlueGoal
from unittest import main, TestCase


class TestStateListener(StateListener):
    def __init__(self):
        self.captured_events = []

    def get_captured_events(self):
        return self.captured_events

    def event_happened(self, event):
        self.captured_events.append(event)


class StateTest(TestCase):

    def test_should_fire_listener_when_red_team_scores(self):
        # given
        test_listener = TestStateListener()
        state = State([test_listener])

        # when
        state.red_scores()

        # then
        self.assertEqual(len(test_listener.get_captured_events()), 1)
        self.assertTrue(isinstance(test_listener.get_captured_events()[0], RedGoal))

    def test_should_fire_listener_when_blue_team_scores(self):
        # given
        test_listener = TestStateListener()
        state = State([test_listener])

        # when
        state.blue_scores()

        # then
        self.assertEqual(len(test_listener.get_captured_events()), 1)
        self.assertTrue(isinstance(test_listener.get_captured_events()[0], BlueGoal))

    def test_should_count_blue_goals(self):
        # given
        state = State()

        # when
        state.blue_scores()

        # then
        self.assertEqual(state.get_blue_goals(), 1)
        self.assertEqual(state.get_current_score().get_blue_goals(), 1)

    def test_should_count_red_goals(self):
        # given
        state = State()

        # when
        state.red_scores()

        # then
        self.assertEqual(state.get_red_goals(), 1)
        self.assertEqual(state.get_current_score().get_red_goals(), 1)

    def test_should_attach_listeners(self):
        # given
        test_listener = TestStateListener()
        state = State()

        # when
        state.attach(test_listener)
        state.blue_scores()

        # then
        self.assertEqual(len(test_listener.get_captured_events()), 1)
        self.assertTrue(isinstance(test_listener.get_captured_events()[0], BlueGoal))


if __name__ == "__main__":
    main()
